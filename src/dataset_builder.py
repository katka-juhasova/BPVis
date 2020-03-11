import os
from module_handler import ModuleHandler
from console_progressbar import ProgressBar


def main():

    path = '/home/katka/Desktop/FIIT/BP/BPVis/data'
    files = list()

    # r=root, d=directories, f = files
    # list all json files
    for r, d, f in os.walk(path):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))

    pb = ProgressBar(total=len(files), prefix='0 files', suffix='{} files'.format(len(files)),
                     decimals=2, length=50, fill='X', zfill='-')
    progress = 0

    # make input for all .json files
    for file in files:
        module_handler = ModuleHandler(file)
        all_nodes = module_handler.get_all_nodes()
        terminals = module_handler.get_terminals()
        paths = module_handler.get_paths()
        context_paths = module_handler.get_context_paths()
        # print('\n' + file)
        # print(all_nodes)
        # print(terminals)
        # print(paths)
        # print(context_paths)
        # print('==================================================')

        # update progress bar
        progress += 1
        pb.print_progress_bar(progress)

    # module_handler = ModuleHandler(files[0])
    # print(files[0])
    # all_nodes = module_handler.get_all_nodes()
    # terminals = module_handler.get_terminals()
    # paths = module_handler.get_paths()
    # context_paths = module_handler.get_context_paths()
    # print(all_nodes)
    # print(terminals)
    # print(paths)
    # print(context_paths)


if __name__ == '__main__':
    main()
