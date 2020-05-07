#!/usr/bin/env python
# coding: utf-8

# In[1]:


import git
from github import Github
import os
import hashlib


# In[2]:


# input

OriginGitHubRepo = 'sPHENIX-Test/coresoftware'
UploadGitHubRepo = 'blackcathj/coresoftware'

GIT_URL = f'git@github.com:{OriginGitHubRepo}.git'
ghprbAuthorRepoGitUrl = 'git@github.com:blackcathj/coresoftware.git'
GIT_UPLOAD_REPOSITORY = f'git@github.com:{UploadGitHubRepo}.git'
WORKSPACE = os.getcwd();
PullRequestID = '1'

print(f'WORKSPACE={WORKSPACE}')


# In[6]:


# local constants
WorkBranchName = f'CheckBranch_pr{PullRequestID}'
MergeBranchName = f'CheckBranch_pr{PullRequestID}_merge'
OriginMasterBranch = 'origin_master'

GitAuthor='sphenix-bot';

ClangFormatCmd = '/cvmfs/sphenix.sdcc.bnl.gov/x8664_sl7/opt/sphenix/utils/bin/clang-format'
SourceFileExtension =['.cpp' , '.cc' , '.cxx', 'C', '.c' , '.h' , '.hpp' , '.hxx' , '.hh'];

os.environ['GIT_PYTHON_TRACE'] = 'full'
import logging
logging.basicConfig(level=logging.INFO)


# In[7]:


repo = git.Repo.clone_from(GIT_URL, os.path.join(WORKSPACE, 'coresoftware'), branch='master')
repo.create_remote('upload', GIT_UPLOAD_REPOSITORY)


# In[8]:


repo.heads.master.checkout()

repo.git.fetch('--force','origin', f'master:{OriginMasterBranch}')
# repo.remotes.origin.fetch(refspec=f'pull/{PullRequestID}/head:{WorkBranchName}', verbose=True,'--force')
repo.git.fetch('--force','origin', f'pull/{PullRequestID}/head:{WorkBranchName}')
repo.git.fetch('--force','origin', f'pull/{PullRequestID}/merge:{MergeBranchName}')
repo.remotes.origin.fetch(verbose=True)
repo.heads[WorkBranchName].checkout()


# In[9]:


print(repo.heads)


# In[10]:


pr_commit = repo.heads[WorkBranchName].commit
pr_merge_commit = repo.heads[MergeBranchName].commit
master_commit = repo.heads[OriginMasterBranch].commit


# In[11]:


changed_files = [];

# ’A’ for added paths
# ’D’ for deleted paths
# ’R’ for renamed paths
# ’M’ for paths with modified data
# ’T’ for changed in the type paths

for diff_added in master_commit.diff(pr_merge_commit).iter_change_type('A'):
    print('Add ',diff_added.b_path)
    changed_files.append(diff_added.b_path) 
for diff_added in master_commit.diff(pr_merge_commit).iter_change_type('R'):
    print('renamed ',diff_added.b_path)
    changed_files.append(diff_added.b_path) 
for diff_added in master_commit.diff(pr_merge_commit).iter_change_type('M'):
    print('modified ',diff_added.b_path)
    changed_files.append(diff_added.b_path) 
    


# In[12]:


updated_files = [];

for file in changed_files:
    print(f'Processing {file}...')
    
    filename, file_extension = os.path.splitext(file)
    if file_extension not in SourceFileExtension :
        print(f'ignore non C++ file {file}')
        continue
    
    full_path_filename = os.path.join( repo.working_dir, file)
    
    print(os.popen(f'ls -lhv {full_path_filename}').read())
    originalmd5 = hashlib.md5(open(full_path_filename,'rb').read()).hexdigest()
    
    os.system(f'{ClangFormatCmd} -i {full_path_filename}')
    
    newmd5 = hashlib.md5(open(full_path_filename,'rb').read()).hexdigest()
    
    if originalmd5 == newmd5:
        print ('No changes')
    else:
        print ('file edited. committing...')
        repo.git.commit('-m','automatic clang-format',file)
        updated_files.append(file)
        
    


# In[13]:


print('updated_files =', updated_files);
len(updated_files)


# In[17]:


# git push

if len(updated_files)>0 :
#     pushinfo=repo.remotes.upload.push(WorkBranchName,None,'-f')
    pushinfo=repo.git.push('upload', WorkBranchName,'-f')
    


# In[ ]:



#########################
# Input and checks
#########################

# GIT_URL = os.environ['GIT_URL']
# GIT_COMMIT = os.environ['GIT_COMMIT']
# src_FilePath = os.environ['src_FilePath']

githubComment = ''

# with open(src_FilePath, 'r') as content_file:
#     githubComment = content_file.read()
# if len(githubComment) == 0:
# 	print('Failed to obtain comments from ', githubComment)
# 	exit(0)
	

# ghprbPullLinkItems = GIT_URL.split('/')

# RepoGit = ghprbPullLinkItems[-1];
# organizationName = ghprbPullLinkItems[-2];
# repoName = (RepoGit.split('.'))[0]

# print("Processing pull request {} -> {}.{} #{} " . format(GIT_URL, organizationName, repoName, GIT_COMMIT) );

with open (os.environ['HOME'] + "/.ssh/github.jenkins.token", "r") as myfile:
	tokens=myfile.readlines()
assert len(tokens) == 1, 'Failed to read tokens : %s' % tokens
token = tokens[0].replace('\n', '');

#########################
# Talk to GitHub
#########################

gh = Github(token)

user = gh.get_user()
print("User name - ", user.name);

org = gh.get_organization(organizationName)
repo = org.get_repo(repoName)
commitObj = repo.get_commit(GIT_COMMIT)

if (len(githubComment)>0):
	print ("Create comment -", githubComment);
	commitObj.create_comment(githubComment)


# In[3]:


os.environ


# In[5]:


os.system('which cpp-check')


# In[6]:


os.system('ls')


# In[8]:


print(os.popen('which cpp-check').read())


# In[9]:


print(os.popen('pwd').read())


# In[25]:


repo.working_dir


# In[14]:


dir(repo)


# In[ ]:




