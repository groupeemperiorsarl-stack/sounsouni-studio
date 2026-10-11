import json, os, subprocess, sys, time
job, lid = sys.argv[1], sys.argv[2]
J = json.load(open(f'jobs/{job}/job.json'))
L = [l for l in J['lines'] if l['id'] == lid][0]
step = max(1, round(25 / J.get('fps', 25)))
d = os.path.abspath(f'jobs/{job}')
out = os.path.abspath(f'out/{lid}')
env = dict(os.environ, JV_FRAMES=out, JV_STEP=str(step), OMP_NUM_THREADS=str(os.cpu_count()))
t = time.time()
r = subprocess.run(['python', 'inference.py', '-r', f"{d}/{L['image']}", '-a', f"{d}/{L['audio']}", '--animation_mode', 'human',
    '--cfg_scale', '2.0', '--flag-force-cpu', '--no-flag-use-half-precision', '--flag-pasteback', '--flag-do-crop', '--flag-stitching',
    '-o', '/tmp/vid'], cwd='jv', env=env)
print('réplique', lid, 'pas', step, 'durée', round(time.time() - t), 's', 'code', r.returncode)
sys.exit(r.returncode)
