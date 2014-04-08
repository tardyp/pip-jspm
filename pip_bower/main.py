import argparse
import sys
import os
import json
import copy
import shutil
import subprocess
import tempfile
import zipfile

def find_bower():
    me = sys.argv[0]
    for path in os.environ["PATH"].split(":"):
        bower = os.path.join(path, "bower")
        if os.path.exists(bower) and bower != me:
            return bower
    print >>sys.stderr, "'bower' not found in PATH"
    sys.exit(1)

def bower(args):
    bower = find_bower()
    os.execv(bower, [bower] + args.args)

def bower_version_to_pip(v):
    if v.startswith("~"):
        v = v[1:].split(".")
        if len(v) > 2:
            high = copy.copy(v)
            high[2] = "0"
            high[1] = str(int(v[1]) + 1)
            return ">="  + ".".join(v) + ",<" + ".".join(high)
    elif v.startswith(">") or v.startswith("<") or v.startswith("="):
        return v
    elif v == "latest":
        return ""
    else:
        return "==" + v

def get_bower_json():
    for fn in ["bower.json", ".bower.json"]:
        if os.path.exists(fn):
            return fn
    print >>sys.stderr, "no 'bower.json' file found"
    sys.exit(1)

def get_bower_deps(args):
    deps = {}
    with open(get_bower_json()) as f:
        bowerjson = json.load(f)
        deps.update(bowerjson["dependencies"])
        if not args.production and 'devDependencies' in bowerjson:
            deps.update(bowerjson["devDependencies"])
    return deps

def install(args):
    pip_args = []
    if "PIP_ARGS" in os.environ:
        pip_args = os.environ["PIP_ARGS"].split(" ")

    for p, v in get_bower_deps(args).items():
        pip_args.append("bower-" + p + bower_version_to_pip(v))
    print "installing", pip_args
    os.execvp("pip", ["pip", "install"] + pip_args)

def zipdir(path, zipf):
    zip = zipfile.ZipFile(zipf, 'w')
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))
    zip.close()

def generate(args):
    deps = get_bower_deps(args)
    bower = find_bower()
    dstdir = os.getcwd()
    os.chdir(tempfile.mkdtemp())
    for p, v in deps.items():
        try:
            shutil.rmtree('bower_components')
        except:
            pass
        subprocess.call([bower, "install", p + "#" + v])
        zipdir(dstdir, os.path.join(dstdir, p + "-" + v + ".zip"))

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    sparser = subparsers.add_parser('bower', help='call original bower')
    sparser.add_argument('args', nargs=argparse.REMAINDER)
    sparser.set_defaults(func=bower)
    sparser = subparsers.add_parser('install', help='install packages required by bower.json')
    sparser.add_argument('-p', '--production', action='store_true')
    sparser.set_defaults(func=install)
    sparser = subparsers.add_parser('generate', help='generate packages required by bower.json')
    sparser.add_argument('-p', '--production', action='store_true')
    sparser.set_defaults(func=generate)
    ret = parser.parse_args()
    ret.func(ret)

if __name__ == '__main__':
    main()
