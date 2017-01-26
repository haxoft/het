
var apiUrlPrefix = "api/";
var app = {};

function expandCollapse(element) {
    var self = $(element);
    self.siblings().toggle();
}

(function() {

    //uncomment to run in atlassian!
    // var getUrlParam = function (param) {
    //     var codedParam = (new RegExp(param + '=([^&]*)')).exec(window.location.search)[1];
    //     return decodeURIComponent(codedParam);
    // };
    //
    // var baseUrl = getUrlParam('xdm_e') + getUrlParam('cp');
    // var options = document.getElementById('connect-loader').getAttribute('data-options');
    //
    // var script = document.createElement("script");
    // script.src = baseUrl + '/atlassian-connect/all.js';
    //
    // if(options) {
    //     script.setAttribute('data-options', options);
    // }
    //
    // document.getElementsByTagName("head")[0].appendChild(script);

    initDocumentTable();
    initNewProjectDialog();
    initNewFolderDialog();
    initImportDialog();
    initExportDialog();
    initRunAnalysis();
    initProjects();
    initRequirements();
})();

function initDocumentTable() {
    new AJS.RestfulTable({
        autoFocus: true,
        el: jQuery("#documents_table"),
        resources: {
            all: apiUrlPrefix + "projects/1/documents",
            self: apiUrlPrefix + "projects/1/documents"
        },
        columns: [
            {
                id: "name",
                header: "Name",
                allowEdit: true
            },
            {
                id: "type",
                header: "Type",
                allowEdit: false
            },
            {
                id: "size",
                header: "Size",
                allowEdit: false
            },
            {
                id: "category",
                header: "Category",
                allowEdit: true
            }
        ],
        allowCreate: true,
        allowEdit: true,
        allowDelete: true,
        createPosition: "bottom",
        deleteConfirmation: true
    });
}

function initNewProjectDialog() {
    AJS.$("#new_project_button").click(function() {
        AJS.dialog2("#new_project_dialog").show();
    });

    AJS.$("#new_project_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#new_project_dialog").hide();
    });

    AJS.$("#new_project_dialog_submit_button").click(function() {
        var input = AJS.$("#new_project_name").val();
        if (input == "") showErrorMessage("Please provide a name for the new project.");
        AJS.$.ajax({
            url: apiUrlPrefix + "/projects",
            method: "POST",
            dataType: "application/json",
            data: input,
            success: function() {
                AJS.dialog2("#new_project_dialog").hide();
                showSuccessMessage("The Project was successfully created.");
            },
            error: function() {
                showErrorMessage("We could not create the project, please try again or contact our webmaster.");
            }
        });
    });
}

function initNewFolderDialog() {
    AJS.$("#new_folder_button").click(function() {
        AJS.dialog2("#new_folder_dialog").show();
    });

    AJS.$("#new_folder_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#new_folder_dialog").hide();
    });

    AJS.$("#new_folder_dialog_submit_button").click(function() {
        var name = AJS.$("#new_project_name").val();
        if (name == "") showErrorMessage("Please provide a name for the new project.");
        AJS.$.ajax({
            url: apiUrlPrefix + "/folders",
            method: "POST",
            dataType: "application/json",
            data: name,
            success: function() {
                AJS.dialog2("#new_project_dialog").hide();
                showSuccessMessage("The Folder was successfully created.");
            },
            error: function() {
                showErrorMessage("We could not create the folder, please try again or contact our webmaster.");
            }
        });
    });
}

function initImportDialog() {
    AJS.$("#import_button").click(function() {
        AJS.dialog2("#import_dialog").show();
    });

    AJS.$("#import_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#import_dialog").hide();
    });

    AJS.$("#import_dialog_submit_button").click(function() {
        var fileData = $('#import_file').prop('files')[0];
        var formData = new FormData();
        form_data.append('file', file_data);
        AJS.$.ajax({
            url: apiUrlPrefix + "/projects/import",
            method: "POST",
            data: formData,
            success: function() {
                showSuccessMessage("Project was imported successfully.");
            },
            error: function() {
                showErrorMessage("An error occured while importing the project, please try again or contact our webmaster.");
            }
        });
    });
}

function initExportDialog() {
    AJS.$("#export_button").click(function() {
        AJS.dialog2("#export_dialog").show();
    });

    AJS.$("#export_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#export_dialog").hide();
    });

    AJS.$("#export_dialog_submit_button").click(function() {
        AJS.$.ajax({
            url: apiUrlPrefix + "/projects",
            method: "GET",
            success: function() {
                showSuccessMessage("Here's your project export");
            },
            error: function() {
                showErrorMessage("An error occured while importing the project, please try again or contact our webmaster.");
            }
        });
    });
}

function initRunAnalysis() {
    $("#run_analysis_button").click(function() {
        //TODO
    });
}

function initProjects() {
    app.Project = Backbone.Model.extend({
        defaults: {
            id: 0,
            name: "",
            requirementsExtracted: false
        },
        url: apiUrlPrefix + "projects"
    });

    app.Folder = Backbone.Model.extend({
        defaults: {
            id: 0,
            name: "",
            folders: [],
            projects: []
        },
        url: apiUrlPrefix + "folders"
    });

    app.ProjectList = Backbone.Collection.extend({
        model: app.Project,
        url: apiUrlPrefix + "projects"
    });

    app.FolderList = Backbone.Collection.extend({
        model: app.Folder,
        url: apiUrlPrefix + "folders"
    });

    function parseProjectList(projectArr) {
        var result = new app.ProjectList([]);
        _.each(projectArr, function(projectObj) {
            var project = new app.Project({id: projectObj.id, name: projectObj.name, requirementsExtracted: projectObj.requirementsExtracted});
            result.add(project);
        });
        return result;
    }

    function parseFolderList(folderArr) {
        var result = new app.FolderList([]);
        _.each(folderArr, function(folderObj) {
            var subFolders = parseFolderList(folderObj.folders);
            var projects = parseProjectList(folderObj.projects);
            var folder = new app.Folder({id: folderObj.id, name: folderObj.name, folders: subFolders, projects});
            result.add(folder);
        });
        return result;
    }

    app.FolderTemplate = _.template($("#folder_template").html());
    app.ProjectTemplate = _.template($("#project_template").html());

    app.ProjectsView = Backbone.View.extend({
        el: "#projects",

        initialize: function(){
            var self = this;
            $.ajax({
                url: apiUrlPrefix + "projects",
                method: "GET",
                success: function(response) {
                    app.projectFolders = parseFolderList(JSON.parse(response));
                    self.render();
                }
            });
        },

        render: function(){
            var result = "";
            app.projectFolders.each(function(folder) {
                result += app.FolderTemplate(folder.attributes);
            });
            this.$el.html(result);
        }
    });

    new app.ProjectsView();
}

function initRequirements() {
    app.Requirement = Backbone.Model.extend({
        defaults: {
            id: 0,
            name: "",
            values: []
        },
        url: apiUrlPrefix + "requirements"
    });

    app.RequirementList = Backbone.Collection.extend({
        model: app.Requirement,
        url: apiUrlPrefix + "requirements"
    });

    function parseRequirementList(requirementArr) {
        var result = new app.RequirementList([]);
        _.each(requirementArr, function(requirementObj) {
            var requirement = new app.Requirement({id: requirementObj.id, name: requirementObj.name, values: requirementObj.values});
            result.add(requirement);
        });
        return result;
    }

    app.RequirementTemplate = _.template($("#requirement_template").html());

    app.RequirementsView = Backbone.View.extend({
        el: "#requirements",

        initialize: function(){
            var self = this;
            $.ajax({
                url: apiUrlPrefix + "projects/1/requirements",
                method: "GET",
                success: function(response) {
                    app.requirements = parseRequirementList(JSON.parse(response));
                    self.render();
                }
            });
        },

        render: function(){
            var result = "";
            app.requirements.each(function(requirement) {
                result += app.RequirementTemplate(requirement.attributes);
            });
            this.$el.html(result);
        }
    });

    new app.RequirementsView();
}
