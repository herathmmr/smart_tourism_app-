import os
import pandas as pd

def create_manifest():
    data = {'filepath': [], 'label': [], 'label_name': []}

   
    crowd_dir = 'data/crowd'
    if os.path.exists(crowd_dir):
        for file in os.listdir(crowd_dir):
            if file.endswith('.wav'):
                data['filepath'].append(f"{crowd_dir}/{file}")
                data['label'].append(0)
                data['label_name'].append('crowd')

  
    nature_dir = 'data/nature'
    if os.path.exists(nature_dir):
        for file in os.listdir(nature_dir):
            if file.endswith('.wav'):
                data['filepath'].append(f"{nature_dir}/{file}")
                data['label'].append(1)
                data['label_name'].append('nature')

    
    df = pd.DataFrame(data)
    df.to_csv('dataset_manifest.csv', index=False)
    print(f"Great! Found {len(df)} files. Successfully updated 'dataset_manifest.csv'!")

if __name__ == '__main__':
    create_manifest()