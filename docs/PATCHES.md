# Work with PuMA pipeline

In order to be able to extract information using softwares such as TEMPO and PRESTO on observations performed
with the two telescopes from IAR, some modifications must be performed on the source codes of these programs.
Here we describe which files need to be changed and how to do them.

Before doing it, be sure to have the repositories of both TEMPO and PRESTO updated to (at least) March 30, 2020.


## TEMPO

On TEMPO we just need to update the file `obsys.dat` by simply adding information on the two telescopes.
For that just use the path named `obsys.patch`, copy it to TEMPO main folder and run:

```
patch < obsys.patch
```

After running the above command, one line should have been replaced while a new one is added.

## PRESTO

Regarding PRESTO sofware, we need to modify several files. Assuming we are in the main folder of it:

 1. `bin/get_TOAS.py`: copy `get_TOAs.patch` to bin/ folder and apply the path `patch < get_TOAs.patch`
 which add information on IAR telescopes to a dictionary called _scopes2_
 
 2. `python/presto/rfifind.py`: same strategy as above, copy patch to the right folder (python/presto/)
 and then patch file (`patch < rfifind.patch`). Here the method called read_byte_mask is added

 3. `src/misc_utils.c`: after doing the same with `patch < misc_utls.patch`, strings for IAR telescopes
 are added to telescope_to_tempocode function

 4. `src/polycos.c`: same as 3., string addition to make_polycos function after running the patch
 `patch < polycos.patch`

 5. 'src/sigproc_fb.c': last patch to perform which in addition to the telescopes ids, there is a
 modification to get_backend_name to consider _Ettus-B205_. It is also done with the following command
 (after copying the corresponding patch to the the src/ folder): `patch < sigproc_fb.patch`


## After patching files

Once all the above listed files are patched, the .patch can be deleted. Then both TEMPO and PRESTO need
to be compiled again:

### TEMPO

Change to TEMPO main folder (cd $TEMPO, if $TEMPO has been added as an environment variable) and do:
`./configure`, followed by `./configure --prefix=/path/to/tempo/` (e.g., --prefix=/opt/pulsar/tempo),
and then `make && make install`. Lastly, `cd util/print_resid && make`

### PRESTO

Go to PRESTO main folder, then `cd src` and run: `make prep && make`. If one wants to add python
packages, go back to PRESTO main folder and run `pip install .` (--user flag for no root users)
