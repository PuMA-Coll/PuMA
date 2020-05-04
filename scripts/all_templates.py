import glob

pulsars = glob.glob('J*')

for psr in pulsars:
    if 'J0437' not in psr:
        print('Creating template for psr ' + psr)
        subprocess.check_call('puma_template.py', cwd=psr)


