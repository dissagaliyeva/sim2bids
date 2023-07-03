# import os
# import shutil
# from sim2bids.generate import subjects
# from sim2bids.app import utils
# from sim2bids.convert import mat
#
#
# def preprocess(path, files, input_path='inputs'):
#     # set to true if there were changes made
#     changed = False
#
#     if os.path.exists(input_path):
#         shutil.rmtree(input_path)
#
#     # create directory if doesn't exist
#     if not os.path.exists(input_path):
#         os.mkdir(input_path)
#
#     # check if the "files" is a single directory, if so
#     # change the path to that folder storing all files
#     if len(files) == 1 and os.path.isdir(path, files[0]):
#         path = os.path.join(path, files[0])
#
#     # iterate over contents and see which input type is passed
#     # 1. get all files
#     content = utils.get_content(path, files) if len(files) > 1 else utils.get_content(path, '')
#
#     # 2. check for unique IDs
#     matches = subjects.find_matches(content)
#
#     if len(matches) > 0:
#         changed = True
#         transfer_files(content, matches, path, input_path)
#
#     if changed:
#         return input_path
#     return None
#
#
# def transfer_files(content, matches, path, input_path):
#     transferred, mat_files = [], {}
#     sid = 0
#
#     def get_files(con, match):
#         return [c for c in con if match in c]
#
#     for match in matches:
#         sid += 1
#
#         files = get_files(content, match)
#
#         # create directory if doesn't exist
#         p = os.path.join(input_path, str(sid))
#
#         if not os.path.exists(p):
#             os.mkdir(p)
#
#         for file in files:
#             transferred.append(file)
#             result = subjects.get_name(file)
#
#             if isinstance(result, str):
#                 shutil.copy(file, os.path.join(input_path, str(sid), result + '.txt'))
#
#     # transfer global files
#     for file in list(set(content).difference(transferred)):
#         shutil.copy(file, input_path)
#
#     # extract content from matlab files
#     for k, v in mat_files.items():
#         mat.save_mat(mat_files[k], os.path.dirname(mat_files[k]['path']), extract=True)
#
