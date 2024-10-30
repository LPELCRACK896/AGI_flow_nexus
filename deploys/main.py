import subprocess

scripts = [
    "dp_etl_satellite_images.py",
    "dp_etl_satellite_images_last_ten_days.py",
    "dp_etl_satellite_images_per_area.py"
]

processes = [subprocess.Popen(["python", script]) for script in scripts]

for p in processes:
    p.wait()
