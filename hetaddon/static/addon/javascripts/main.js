var apiUrlPrefix = "api/";
var app = {};

function showSuccessMessage(message) {
    console.log(message);
}

function showErrorMessage(message) {
    console.error(message);
}

function showConfirmationMessage(message, callback) {
    alert(message);
    callback();
}

function expandCollapse(element) {
    var self = $(element);
    self.siblings().toggle();
}

function addDocument() {
    $('#add_document_file').trigger("click");
}

function uploadDocument(element) {
    var file = element.files[0];
    if (file) {
        var reader = new FileReader();
        reader.readAsBinaryString(file);
        reader.onload = function (event) {
            var content = event.target.result;
            var size = file.size;
            var type = file.name.indexOf('.') != -1 ? file.name.split('.').pop() : "";
            var data = {
                name:"New Document",
                size:size,
                type:type,
                content:btoa(content),
                category:"oth",
                project_id:1
            };
            $.ajax({
                url: apiUrlPrefix + "documents",
                method: "POST",
                data: JSON.stringify(data),
                success: function(response) {
                    showSuccessMessage("The Document was uploaded successfully");
                    app.documents.fetch();
                },
                error: function(xhr, status, err) {
                    showErrorMessage("The document could not be uploaded, please try again or contact our webmaster.");
                }
            });
        };
        reader.onerror = function (event) {
            showErrorMessage("Could not read document file.")
        };
    }
}

function deleteDocument(documentId) {
    showConfirmationMessage("Delete this document?", function(){
        app.documents.remove(documentId);
    });
}

function addSection() {
    var data = {
        name:"New Section",
        project_id:1
    }
    $.ajax({
        url: apiUrlPrefix + "sections",
        method: "POST",
        data: JSON.stringify(data),
        success: function(response) {
            showSuccessMessage("The Section was created successfully");
            app.documents.fetch();
        },
        error: function(xhr, status, err) {
            showErrorMessage("The section could not be created, please try again or contact our webmaster.");
        }
    });
}

(function() {
    /*var getUrlParam = function (param) {
        var codedParam = (new RegExp(param + '=([^&]*)')).exec(window.location.search)[1];
        return decodeURIComponent(codedParam);
    };
    var baseUrl = getUrlParam('xdm_e') + getUrlParam('cp');
    var options = document.getElementById('connect-loader').getAttribute('data-options');
    var script = document.createElement("script");
    script.src = baseUrl + '/atlassian-connect/all.js';
    if(options) {
        script.setAttribute('data-options', options);
    }

    document.getElementsByTagName("head")[0].appendChild(script);*/

    initDocumentTable();
    initNewProjectDialog();
    initNewFolderDialog();
    initImportDialog();
    initExportDialog();
    initRunAnalysis();
    initProjects();
    initRequirements();

    setInterval(function(){
        app.projectFolders.fetch();
        app.requirements.fetch();
        app.documents.fetch();
    },15000);
})();

function initDocumentTable() {
    app.Document = Backbone.Model.extend({
        defaults: {
            id: 0,
            name: "",
            type: "",
            size: 0,
            category: "oth"
        },
        url: apiUrlPrefix + "documents"
    });

    app.DocumentList = Backbone.Collection.extend({
        model: app.Document,
        url: apiUrlPrefix + "projects/1/documents"
    });

    function parseDocumentList(documentArr) {
        var result = new app.DocumentList([]);
        _.each(documentArr, function(documentObj) {
            var document = new app.Document({id: documentObj.id, name: documentObj.name, type: documentObj.type,
                size: documentObj.size, category: documentObj.category});
            result.add(document);
        });
        return result;
    }

    app.DocumentsView = Backbone.View.extend({
        el: "#document_table_rows",

        initialize: function(){
            var self = this;
            $.ajax({
                url: apiUrlPrefix + "projects/1/documents",
                method: "GET",
                success: function(response) {
                    app.documents = parseDocumentList(response);
                    app.documents.on('reset',self.render(),self);
                    self.render();
                }
            });
        },

        render: function(){
            app.DocumentRowTemplate = _.template($("#document_row_template").html());
            var result = "";
            app.documents.each(function(document) {
                result += app.DocumentRowTemplate(document.attributes);
            });
            this.$el.html(result);
        }
    });

    new app.DocumentsView();
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
            var folder = new app.Folder({id: folderObj.id, name: folderObj.name, folders: subFolders, projects: projects});
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
                url: apiUrlPrefix + "folders",
                method: "GET",
                success: function(response) {
                    app.projectFolders = parseFolderList(response);
                    app.projectFolders.on('reset',self.render(),self);
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
        url: apiUrlPrefix + "projects/1/requirements"
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
                    app.requirements = parseRequirementList(response);
                    app.requirements.on('reset',self.render(),self);
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