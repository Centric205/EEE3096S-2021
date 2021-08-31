import subprocess

compile = "make"
run = "run"
thread = "threaded"
run_thread = "run_threaded"
subprocess.call([compile])
print(" ")

for i in range(10):
	subprocess.call([compile, run])
	print(" ")
