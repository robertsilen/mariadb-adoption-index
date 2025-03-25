import os
import csv

def extract_cron_schedules():
    workflows_dir = '.github/workflows'
    output_file = 'workflow_overview/workflow_schedules.csv'
    
    # Create a list to store results
    schedules = []
    
    # Go through all yml files in workflows directory
    for filename in os.listdir(workflows_dir):
        if filename.endswith('.yml'):
            filepath = os.path.join(workflows_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                cron = ''
                time = ''
                month = ''
                secrets = ''   
                # Go through each line looking for cron
                for line in content.split('\n'):
                    if 'cron:' in line:
                        # Split the line and get the schedule part
                        cron = line.split("cron:")[1].strip()
                        cron = cron.split("#")[0].strip()
                        cron = cron.replace("'", "").replace('"', '')
                        break  # Only get the first cron entry per file
                # Go through each line looking for secrets
                for line in content.split('\n'):
                    if 'secrets.' in line:
                        secrets = line.split('secrets.')[1].strip()
                        secrets = secrets.split(' ')[0].strip()
                        break
                time = cron.split(' ')[1].strip()+":"+cron.split(' ')[0].strip()
                month = cron.split(' ')[2].strip()
                item = [filename, cron, time, month, secrets]
                print(item)
                schedules.append(item)

    # order schedules by filename
    schedules.sort(key=lambda x: x[0])

    # Write results to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'cron', 'time', 'month', 'secrets'])  # Write header
        writer.writerows(schedules)

if __name__ == '__main__':
    extract_cron_schedules()
