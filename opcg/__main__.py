#!/usr/bin/python

# Standard library imports
from datetime import datetime
import subprocess
import argparse
import json
import os
import re 

# Application imports
from generator import augmentProgram, genKernelHost
from language import Lang
from parallelization import Para
from parsers.common import Store


# Program entrypoint
def main(argv=None):
  global args

  # Build arg parser
  parser = argparse.ArgumentParser(prog='w.i.p')
  parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=getVersion())
  parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
  parser.add_argument('-o', '--out', help='Output Directory', type=isDirPath, default='.')
  parser.add_argument('-p', '--prefix', help='Output File Prefix', type=isValidPrefix, default='op_')
  # parser.add_argument('-l', '--language', help='Target Language', type=str, choices=Lang.())
  parser.add_argument('-soa', '--soa', help='Structs of Arrays', action='store_true')
  parser.add_argument('para', help='Target Parallelization', type=str, choices=Para.names())
  parser.add_argument('file_paths', help='Input Files', type=isFilePath, nargs='+')
  args = parser.parse_args(argv)

  # Collect the set of file extensions
  extensions = { os.path.splitext(path)[1][1:] for path in args.file_paths }

  # Validate the file extensions
  if not extensions:
    raise Exception('Missing file extensions, unable to determine target language.')

  elif len(extensions) > 1:
    raise Exception('Varying file extensions, unable to determine target language.')

  else:
    [ extension ] = extensions 

  # Determine the target language and parallelisation
  para = Para.find(args.para)
  lang = Lang.find(extension)

  if not lang:
    raise Exception(f'Unsupported file extension: {extension}')

  if args.verbose:
    print(f'Target language: {lang}')
    print(f'Target parallelization: {para}\n')

  # TODO: Lookup translation scheme using (l, p)
  scheme = None




  # ---                   Source Parsing                    --- #




  main_store = Store()

  # Parse the input files
  for i, raw_path in enumerate(args.file_paths, 1):

    if args.verbose:
      print(f'Parsing file {i} of {len(args.file_paths)}: {raw_path}')
    
      store = lang.parse(raw_path) 

      if args.verbose:
        print(f'  Parsed: {store}')

      # Fold store
      main_store.merge(store)

  if args.verbose:
    print('\nMain store:', main_store, '\n')

  if not main_store.init:
    raise OpError()

  if not main_store.exit:
    raise OpError()




  # TODO: Remove ...
  kernels = main_store.loops
  with open(os.path.join(args.out, 'consts.json'), 'w') as file:
    file.write(json.dumps(main_store.consts, indent=4))




  # ---                   Code generation                    --- #




  # Collect the paths of any generated files
  generated_paths = [] # TODO: Destroy any generated files after failure

  # Generate kernel parallelisations
  for i, kernel in enumerate(kernels, 1):

    if args.verbose:
      print(f'Generating kernel host {i} of {len(kernels)}: {kernel["kernel"]}')

    # Form output file path 
    path = os.path.join(args.out, args.prefix + kernel['kernel'])

    # Generate kernel source
    source = genKernelHost(kernel, scheme)

    # Write the translated source file
    with open(path, 'w') as file:
      file.write(f'\n{lang.com_delim} Auto-generated at {datetime.now()} by {parser.prog}\n\n')
      file.write(source)
      generated_paths.append(path)

      if args.verbose:
        print(f'  Created kernel host file: {path}')




  # Generate program translations
  for i, raw_path in enumerate(args.file_paths, 1):

    if args.verbose:
      print(f'Translating file {i} of {len(args.file_paths)}: {raw_path}')
    
    # Read the raw source file
    with open(raw_path, 'r') as raw_file:
      source = raw_file.read()

      # Translate the source
      translation = augmentProgram(source, main_store)

      # Form output file path 
      new_path = os.path.join(args.out, args.prefix + os.path.basename(raw_path))

      # Write the translated source file
      with open(new_path, 'w') as new_file:
        new_file.write(f'\n{lang.com_delim} Auto-generated at {datetime.now()} by {parser.prog}\n\n')
        new_file.write(translation)
        generated_paths.append(new_path)

        if args.verbose:
          print(f'  Created translation file: {new_path}')     


  # End of main
  if args.verbose:
    print('\nTerminating')






def getVersion():
  return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


def isDirPath(path):
  if os.path.isdir(path):
    return path
  else:
    raise argparse.ArgumentTypeError(f"invalid dir path: {path}")


def isFilePath(path):
  if os.path.isfile(path):
    return path
  else:
    raise argparse.ArgumentTypeError(f"invalid file path: {path}")


def isValidPrefix(prefix):
  if re.compile(r"^[a-zA-Z0-9_-]+$").match(prefix):
    return prefix
  else:
    raise argparse.ArgumentTypeError(f"invalid output file prefix: {prefix}")


class OpError(Exception):
  pass


if __name__ == '__main__':
  main()