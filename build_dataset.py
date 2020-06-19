import argparse
import random
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default='data/contracts', help="Directory with the smart contracts dataset")
parser.add_argument('--output_dir', default='data/datasets', help="Where to write the new data")

if __name__ == '__main__':
    args = parser.parse_args()

    assert os.path.isdir(args.data_dir), "Couldn't find the dataset at {}.".format(args.data_dir)

    # Define the train/dev/test data directories
    # data_dir = os.path.join(args.data_dir)

    # Get the filenames in each directory (train, dev, and test)
    filenames = os.listdir(args.data_dir)
    filenames = [os.path.join(args.data_dir, f) for f in filenames if f.endswith('.zip')] # ToB_15k only cntains with the extension .zip

    # Split the files into %80 train_files, %10 dev_files, and another %10 test_files
    random.seed(111)
    filenames.sort()
    random.shuffle(filenames)

    split_1 = int(0.8 * len(filenames))
    split_2 = int(0.9 * len(filenames))
    train_filenames = filenames[:split_1]
    dev_filenames = filenames[split_1:split_2]
    test_filenames = filenames[split_2:]

    filenames = {'train': train_filenames,
                 'dev'  : dev_filenames,
                 'test' : test_filenames}
    
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    else:
        print("Warning: output dir {} already exists".format(args.output_dir))
    
    # Preprocess train, dev, and test sets
    for split in ['train', 'dev', 'test']:
        output_dir_split = os.path.join(args.output_dir, '{}_files'.format(split))
        if not os.path.exists(output_dir_split):
            os.mkdir(output_dir_split)
        else:
            print("Warning: dir {} already exists".format(output_dir_split))
        
        print("Processing {} data, saving preprocessed data to {}".format(split, output_dir_split))
        for filename in filenames[split]:
            shutil.move(filename, output_dir_split)
            
    print("Done building dataset")