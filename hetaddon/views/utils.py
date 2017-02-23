from hetaddon.models.data import *


def get_user_from_session(request):

    if 'user' not in request.session:
        return None
    user_session = request.session['user']
    ret_user = User.objects.get(externalplatform__user_ext_id=user_session["userKey"])
    return ret_user


def get_folder_of_project(project, user):
    log.debug('finding the folder of project:' + str(project))
    user_folders_list = get_user_folders(user)
    for i in range(0, len(user_folders_list)):
        project_folder_set = ProjectFolder.objects.filter(project=project, folder=user_folders_list[i])
        if project_folder_set:
            if len(project_folder_set) > 1:
                log.error("Found multiple folders for project! Found ProjectFolders:" + str(project_folder_set))
                return None
            log.debug("Found folder:" + str(project_folder_set[0].folder.id) + ", for project:" + str(project.id))
            return project_folder_set[0].folder
    log.error("Found no folder for project! Project:" + str(project))
    return None


def get_user_folders(user):
    user_root_folders = RootFolder.objects.filter(owner=user)
    user_folders = []
    for root_folder in user_root_folders:
        user_folders.append(root_folder)
        add_subfolders(user_folders, root_folder)
    return user_folders


def add_subfolders(subfolders_list, parent_folder):
    subfolders_set = parent_folder.folder_set.all()
    for i in range(0, len(subfolders_set)):
        subfolders_list.append(subfolders_set[i])
        add_subfolders(subfolders_list, subfolders_set[i])


def user_owns_section(user, section):

    user_projects = Project.objects.filter(membership__user=user)
    for user_project in user_projects:
        if section.project_id == user_project.id:
            return True
    return False


def user_owns_document(user, document):

    user_projects = Project.objects.filter(membership__user=user)
    for user_project in user_projects:
        if document.section.project.id == user_project.id:
            return True
    return False
