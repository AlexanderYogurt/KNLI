import os
import sys
from random import uniform, randrange, choice
import time
import numpy as np
from collections import OrderedDict
import argparse

parser = argparse.ArgumentParser()
# params
parser.add_argument('--model_name', default='BERTse')
parser.add_argument('--description', default='==NEW==', type=str)
parser.add_argument('--gpu', type=str, default='0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15', help='used gpu')
# parser.add_argument('--gpu', type=str, default='0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,14,14,15,15', help='used gpu')
parser.add_argument('--cp',  default=False, action='store_true')
parser.add_argument('--fp_train', default='./data/mnli/mnli_data.json')
parser.add_argument('--fp_val',   default='./data/mnli/mnli_data.json')
parser.add_argument('--fp_embd',  default='./data/glove/glove.840B.300d.txt')
parser.add_argument('--n_epochs', default=6, type=int)
parser.add_argument('--concept_layers', type=str, default='-1')


def create_log_dir(name_log_folder):
    import sys
    cwd = os.getcwd()
    sys.path.append(os.path.abspath(cwd))
    from misc.utilities import create_dir
    create_dir(name_log_folder)

def get_ids(list_gpus):
    '''
    input "1,4,3,2"
    output [1,4,3,2]
    '''
    gpus = list_gpus.split(',')
    gl = []
    for g in gpus:
        gl.append(int(g))

    return gl

def convert_dictTotext(input_param):
    cmd = ""
    for k, v in input_param.items():
        if type(v) == bool:
            if v:
                cmd =  cmd +"--"+k+" "
        else:
            cmd =  cmd +"--"+k+ " "+ str(v)+" "
    return cmd

root_folder_data = '/home/ubuntu/projects/KNLI/'
root_folder_ck   = '/home/ubuntu/projects/KNLI/'

if __name__ == "__main__":
    args = parser.parse_args()
    print(args.__dict__)
    print("-----------------------------------")
    print("-----------------------------------")

    opt = OrderedDict()
    gpu_list = get_ids(args.gpu)
    dataset_path = args.fp_train

    file_id = os.path.join(root_folder_data,'logs/') + "_" + args.model_name + "_" + \
              str(randrange(20)) + "_" +str(int(time.time())) + ".txt"
    opt['fp_train'] = args.fp_train
    opt['fp_val'] = args.fp_val
    opt['fp_embd'] = args.fp_embd
    opt['check_point_dir'] = os.path.join(root_folder_ck, 'check_points')
    opt['n_epochs'] = args.n_epochs
    opt['model_name'] = args.model_name
    opt['description'] = args.description
    opt['concept_layers'] = args.concept_layers

    create_log_dir(os.path.join(root_folder_data,'logs'))

    # start tuning parameters
    with open(file_id, 'w') as f:

      for idx, g in enumerate(gpu_list):

        random_id = str(randrange(10)) + str(int(time.time()))[-6:] # just returns 6 numbers
        opt['log_id'] = random_id

        # not change often
        opt['opt'] = choice(['bert'])
        opt['lr'] = choice([6.25e-5, 1.00e-4])
        opt['lr_warmup'] = choice([0.01, 0.05, 0.10])
        opt['l2']  = choice([0.01])
        opt['hidden_size']  = choice([512])
        opt['heads'] = choice([5]) # divisible for 300
        opt['droprate'] =  choice([0.10])
        opt['val_interval'] = 1
        opt['print_every'] = 2000
        opt['loader_num_workers'] = 4
        opt['checkpoint_every'] = 20
        opt['seed_random'] = 822 #np.random.randint(100, 10000)
        opt['beta1'] = choice([0.5])
        opt['beta2'] = choice([0.999])

        # tune
        opt['num_layers'] = choice([3])
        opt['batch_size'] = choice([16, 32])

        # cmd
        drop = str(opt['droprate']-int(opt['droprate']))[1:][1]
        cmd = 'CUDA_VISIBLE_DEVICES=%d ' % (g, )
        cmd = cmd + 'nohup python -u train_bert.py' + ' '
        cmd = cmd + '' + convert_dictTotext(opt)
        if 'num_layers' in opt:
            log_file = opt['model_name'] + "_" + opt['log_id'] + "_L"+str(opt['num_layers']) +"_D"+str(drop) +".log"
        else:
            log_file = opt['model_name'] + "_" + opt['log_id'] + "_D"+str(drop) +".log"

        cmd = cmd + " > "+ os.path.join(root_folder_data,'logs/') + log_file + " &"
        f.write(cmd + '\n')
        f.write("------------------\n")
        print(cmd)
        print("------------------")
        os.system(cmd)
        time.sleep(2)
      f.close()
