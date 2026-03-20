import importlib.util
import os
import runpy
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name, rel_path, injected_modules=None):
    injected_modules = injected_modules or {}
    saved = {}
    for name, module in injected_modules.items():
        saved[name] = sys.modules.get(name)
        sys.modules[name] = module

    try:
        spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / rel_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


class ScriptSmokeTests(unittest.TestCase):
    def test_copy_db_without_mask_ps_keeps_working(self):
        pandas = types.ModuleType("pandas")
        puma_utils = load_module(
            "test_puma_utils",
            "scripts/puma_utils.py",
            {"pandas": pandas},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "obs"
            dest = tmp / "db"
            source.mkdir()
            (dest / "last_obs").mkdir(parents=True)

            (source / "example_timing.png").write_text("png")
            (source / "example.pfd").write_text("pfd")
            (source / "example.polycos").write_text("polycos")

            with mock.patch.object(puma_utils.subprocess, "check_call") as check_call:
                pngs, pfds, polycos = puma_utils.copy_db("JTEST", "A1", str(source), str(dest))

            self.assertEqual(pngs, ["example_timing.png"])
            self.assertEqual(pfds, ["example.pfd"])
            self.assertEqual(polycos, ["example.polycos"])
            self.assertFalse(check_call.called)
            self.assertTrue((dest / "JTEST" / "pngs" / "example_timing.png").exists())
            self.assertTrue((dest / "JTEST" / "pfds" / "example.pfd").exists())
            self.assertTrue((dest / "JTEST" / "pfds" / "example.polycos").exists())
            self.assertTrue((dest / "last_obs" / "JTEST_A1_timing.png").exists())

    def test_puma_select_pfds_creates_destination_and_moves_low_snr_files(self):
        script_path = REPO_ROOT / "scripts" / "puma_select_pfds.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "good.pfd").write_text("pfd")
            (tmp / "bad.pfd").write_text("pfd")
            (tmp / "bad.pfd.polycos").write_text("polycos")
            (tmp / "bad.pfd.bestprof").write_text("bestprof")

            def fake_check_output(cmd):
                if cmd[-1] == "good.pfd":
                    return b"snr 20\n"
                if cmd[-1] == "bad.pfd":
                    return b"snr 5\n"
                raise AssertionError(cmd)

            old_argv = sys.argv[:]
            old_cwd = os.getcwd()
            try:
                sys.argv = [str(script_path), "10"]
                os.chdir(tmp)
                with mock.patch("subprocess.check_output", side_effect=fake_check_output):
                    runpy.run_path(str(script_path), run_name="__main__")
            finally:
                sys.argv = old_argv
                os.chdir(old_cwd)

            bad_dir = tmp / "no_tan_malas"
            self.assertTrue(bad_dir.is_dir())
            self.assertTrue((bad_dir / "bad.pfd").exists())
            self.assertTrue((bad_dir / "bad.pfd.polycos").exists())
            self.assertTrue((bad_dir / "bad.pfd.bestprof").exists())
            self.assertTrue((tmp / "good.pfd").exists())

    def test_pipe_reduc_uses_cli_par_dirname(self):
        calls = {}

        class FakeObservation:
            def __init__(self, folder):
                self.folder = folder
                self.pname = "JTEST"
                self.antenna = "A1"
                self.maskname = "mask"

            def set_params2reduc(self, **kwargs):
                calls["set_params2reduc"] = kwargs

            def do_reduc(self):
                calls["do_reduc"] = True

            def calc_snr(self, pfd=""):
                calls["calc_snr"] = pfd

            def do_toas(self, **kwargs):
                calls["do_toas"] = kwargs

            def get_mask_percentage(self, maskname):
                calls["get_mask_percentage"] = maskname

        puma_lib = types.ModuleType("puma_lib")
        puma_lib.Observation = FakeObservation

        puma_utils = types.ModuleType("puma_utils")
        puma_utils.copy_db = lambda *args: ([], [], [])
        puma_utils.write_pugliS_info_jason = lambda *args: None

        puma_timing = types.ModuleType("puma_timing")

        def fake_plot_residuals(**kwargs):
            calls["plot_residuals"] = kwargs

        puma_timing.plot_residuals = fake_plot_residuals

        sigproc = types.ModuleType("sigproc")

        module = load_module(
            "test_pipe_reduc",
            "scripts/pipe_reduc.py",
            {
                "puma_lib": puma_lib,
                "puma_utils": puma_utils,
                "puma_timing": puma_timing,
                "sigproc": sigproc,
            },
        )

        with mock.patch.object(module.glob, "glob", return_value=["/obs/result.pfd"]):
            module.do_pipe_reduc(folder="/obs", path2pugliese="/db", par_dirname="/pars")

        self.assertEqual(calls["set_params2reduc"]["par_dirname"], "/pars")
        self.assertEqual(calls["plot_residuals"]["par_fname"], "/pars/JTEST.par")

    def test_pipe_puglis_uses_cli_par_dirname(self):
        calls = {}

        class FakeObservation:
            def __init__(self, folder):
                self.folder = folder
                self.pname = "JTEST"
                self.antenna = "A2"
                self.nfils = 2
                self.red_alert = False
                self.blue_alert = False

            def do_glitch_search(self, **kwargs):
                calls["do_glitch_search"] = kwargs

            def calc_snr(self, pfd=""):
                calls.setdefault("pfds", []).append(pfd)

            def do_toas(self, **kwargs):
                calls["do_toas"] = kwargs

        puma_lib = types.ModuleType("puma_lib")
        puma_lib.Observation = FakeObservation

        puma_utils = types.ModuleType("puma_utils")
        puma_utils.copy_db = lambda *args: ([], [], [])
        puma_utils.write_pugliS_info_jason = lambda *args: None

        puma_timing = types.ModuleType("puma_timing")

        def fake_plot_residuals(**kwargs):
            calls["plot_residuals"] = kwargs

        puma_timing.plot_residuals = fake_plot_residuals

        sigproc = types.ModuleType("sigproc")

        module = load_module(
            "test_pipe_puglis",
            "scripts/pipe_pugliS.py",
            {
                "puma_lib": puma_lib,
                "puma_utils": puma_utils,
                "puma_timing": puma_timing,
                "sigproc": sigproc,
            },
        )

        with mock.patch.object(module.glob, "glob", return_value=["/obs/one.pfd", "/obs/two.pfd"]):
            module.do_pipe_puglis(folder="/obs", thresh=1e-8, path2pugliese="/db", par_dirname="/pars")

        self.assertEqual(calls["do_glitch_search"]["par_dirname"], "/pars")
        self.assertEqual(calls["plot_residuals"]["par_fname"], "/pars/JTEST.par")

    def test_do_glitch_search_uses_target_directory_for_file_discovery(self):
        sigproc = types.ModuleType("sigproc")
        rfifind = types.ModuleType("rfifind")
        psrchive = types.ModuleType("psrchive")

        puma_lib = load_module(
            "test_puma_lib",
            "scripts/puma_lib.py",
            {"sigproc": sigproc, "rfifind": rfifind, "psrchive": psrchive},
        )

        obs = puma_lib.Observation.__new__(puma_lib.Observation)
        obs.was_reduced = False
        obs.read_bestprof = mock.Mock(side_effect=[(1.0, 0.0, 0), (1.0, 0.0, 0)])

        def fake_glob(pattern):
            if pattern == "/target/*timing*.pfd":
                return ["/target/prepfold_timing.pfd"]
            if pattern == "/target/*par*.pfd":
                return ["/target/prepfold_par.pfd"]
            if pattern == "/target/*.mask":
                return ["/target/mask.mask"]
            raise AssertionError(pattern)

        with mock.patch.object(puma_lib.glob, "glob", side_effect=fake_glob):
            ierr = obs.do_glitch_search(path_to_dir="/target")

        self.assertEqual(ierr, 0)
        self.assertEqual(obs.maskname, "/target/mask.mask")
        self.assertFalse(obs.yellow_alert)
        self.assertFalse(obs.red_alert)

    def test_puma_template_moves_generated_std_from_cwd(self):
        script_path = REPO_ROOT / "scripts" / "puma_template.py"
        psrchive = types.ModuleType("psrchive")

        class FakeArchive:
            def __init__(self, filename):
                self._filename = filename

            def get_filename(self):
                return self._filename

        psrchive.Archive_load = lambda filename: FakeArchive("./20200101_obs.pfd")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "20200101_obs.pfd").write_text("pfd")

            def fake_check_output(cmd):
                if cmd[0] == "psrstat":
                    return b"10"
                if cmd[0] == "psrsmooth":
                    (tmp / "20200101_obs.pfd.std").write_text("std")
                    return b""
                raise AssertionError(cmd)

            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                with mock.patch.dict(sys.modules, {"psrchive": psrchive}):
                    with mock.patch("subprocess.check_output", side_effect=fake_check_output):
                        runpy.run_path(str(script_path), run_name="__main__")
            finally:
                os.chdir(old_cwd)

            self.assertTrue((tmp / "Jobs.pfd.std").exists())
            self.assertFalse((tmp / "20200101_obs.pfd.std").exists())


if __name__ == "__main__":
    unittest.main()
