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
                section_id:1
            };
            $.ajax({
                url: apiUrlPrefix + "documents",
                method: "POST",
                data: JSON.stringify(data),
                success: function() {
                    showSuccessMessage("The Document was uploaded successfully");
                    refreshDocuments();
                },
                error: function() {
                    showErrorMessage("The document could not be uploaded, please try again or contact our webmaster.");
                }
            });
        };
        reader.onerror = function () {
            showErrorMessage("Could not read document file.")
        };
    }
}

function deleteDocument(documentId) {
    showConfirmationMessage("Delete this document?", function(){
        $.ajax({
            url: apiUrlPrefix + "documents/" + documentId,
            method: "DELETE",
            success: function() {
                showSuccessMessage("Document deleted");
                refreshDocuments();
            },
            error: function() {
                showErrorMessage("Could not delete document");
            }
        });
    });
}

function addSection() {
    var data = {
        name:"New Section",
        project_id:1
    };
    $.ajax({
        url: apiUrlPrefix + "sections",
        method: "POST",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Section was created successfully");
            refreshDocuments();
        },
        error: function() {
            showErrorMessage("The section could not be created, please try again or contact our webmaster.");
        }
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function refreshDocuments() {
    console.log("Synchronizing Documents");
    app.documents.fetch({reset: true});
}

function refreshProjectFolders() {
    console.log("Synchronizing Folders and Projects");
    app.projectFolders.fetch({reset: true});
}

function refreshRequirements() {
    console.log("Synchronizing Requirements");
    app.requirements.fetch({reset: true});
}

function refreshAll(){
    refreshDocuments();
    refreshProjectFolders();
    refreshRequirements();
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

    $.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });

    initModels();
    initTemplates();
    initCollectionInstances();
    initDocumentTable();
    initProjects();
    initFolderList();
    initRequirements();
    initNewProjectDialog();
    initNewFolderDialog();
    initImportDialog();
    initExportDialog();
    initRunAnalysis();

    refreshAll();
    setInterval(refreshAll,30000);
})();

function initModels() {
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

    app.Project = Backbone.Model.extend({
        defaults: {
            id: 0,
            name: "",
            requirementsExtracted: false
        },
        url: apiUrlPrefix + "projects"
    });

    app.ProjectList = Backbone.Collection.extend({
        model: app.Project
    });

    app.Folder = Backbone.Model.extend({
        initialize: function() {
            var folders = this.get("folders");
            var projects = this.get("projects");
            if (!Array.isArray(folders)) {
                folders = [];
            }
            if (!Array.isArray(projects)) {
                projects = [];
            }
            this.set({folders: new app.FolderList(folders)});
            this.set({projects: new app.ProjectList(projects)});
        },

        defaults: {
            id: 0,
            name: ""
        },
        url: apiUrlPrefix + "folders"
    });

    app.FolderList = Backbone.Collection.extend({
        model: app.Folder,
        url: apiUrlPrefix + "folders"
    });

    app.RequirementValue = Backbone.Model.extend({
        defaults: {
            id: 0,
            data: "",
            disabled: false,
            document_id: 0
        }
    });

    app.RequirementValueList = Backbone.Collection.extend({
        model: app.RequirementValue
    })

    app.Requirement = Backbone.Model.extend({
        initialize: function() {
            var values = this.get("values");
            if (!Array.isArray(values)) {
                values = [];
            }
            this.set({values: new app.RequirementValueList(values)});
        },

        defaults: {
            name: ""
        },
        url: apiUrlPrefix + "requirements"
    });

    app.RequirementList = Backbone.Collection.extend({
        model: app.Requirement,
        url: apiUrlPrefix + "projects/1/requirements"
    });
}

function initTemplates() {
    app.DocumentRowTemplate = _.template($("#document_row_template").html());
    app.FolderOptionTemplate = _.template($("#folder_option_template").html());
    app.FolderTemplate = _.template($("#folder_template").html());
    app.ProjectTemplate = _.template($("#project_template").html());
    app.RequirementTemplate = _.template($("#requirement_template").html());
}

function initCollectionInstances() {
    app.documents = new app.DocumentList();
    app.projectFolders = new app.FolderList();
    app.requirements = new app.RequirementList();
}

function initDocumentTable() {
    app.DocumentsView = Backbone.View.extend({
        el: "#document_table_rows",

        initialize: function(){
            var self = this;
            app.documents.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function(){
            var result = "";
            app.documents.each(function(document) {
                result += app.DocumentRowTemplate({document:document});
            });
            this.$el.html(result);
        }
    });

    app.documentsView = new app.DocumentsView();
}

function initFolderList() {
    app.NewProjectFoldersView = Backbone.View.extend({
        el: "#new_project_folder",

        initialize: function(){
            var self = this;
            app.projectFolders.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function(){
            var result = "";
            app.projectFolders.each(function(folder) {
                result += app.FolderOptionTemplate({currentPath:"",folder:folder});
            });
            this.$el.html(result);
        }
    });

    app.newProjectFoldersView = new app.NewProjectFoldersView();

    app.NewFolderFoldersView = Backbone.View.extend({
        el: "#new_folder_folder",

        initialize: function(){
            var self = this;
            app.projectFolders.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function(){
            var result = "";
            app.projectFolders.each(function(folder) {
                result += app.FolderOptionTemplate({currentPath:"",folder:folder});
            });
            this.$el.html(result);
        }
    });

    app.newFolderFoldersView = new app.NewFolderFoldersView();
}

function initNewProjectDialog() {
    $("#new_project_button").click(function() {
        AJS.dialog2("#new_project_dialog").show();
    });

    $("#new_project_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#new_project_dialog").hide();
    });

    $("#new_project_dialog_submit_button").click(function() {
        var name = $("#new_project_name").val();
        if (name == "") showErrorMessage("Please provide a name for the new project.");
        var parentFolderId = $("#new_project_folder").val();
        var data = {
            name: name,
            parent_folder_id: parentFolderId
        };
        $.ajax({
            url: apiUrlPrefix + "projects",
            method: "POST",
            data: JSON.stringify(data),
            success: function() {
                AJS.dialog2("#new_project_dialog").hide();
                showSuccessMessage("The Project was successfully created.");
                refreshProjectFolders();
            },
            error: function() {
                showErrorMessage("We could not create the project, please try again or contact our webmaster.");
            }
        });
    });
}

function initNewFolderDialog() {
    $("#new_folder_button").click(function() {
        AJS.dialog2("#new_folder_dialog").show();
    });

    $("#new_folder_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#new_folder_dialog").hide();
    });

    $("#new_folder_dialog_submit_button").click(function() {
        var name = $("#new_folder_name").val();
        if (name == "") showErrorMessage("Please provide a name for the new project.");
        var parentFolderId = $("#new_folder_folder").val();
        var data = {
            name: name,
            parent_folder_id: parentFolderId
        };
        $.ajax({
            url: apiUrlPrefix + "folders",
            method: "POST",
            data: JSON.stringify(data),
            success: function() {
                AJS.dialog2("#new_project_dialog").hide();
                showSuccessMessage("The Folder was successfully created.");
                refreshProjectFolders();
            },
            error: function() {
                showErrorMessage("We could not create the folder, please try again or contact our webmaster.");
            }
        });
    });
}

function initImportDialog() {
    $("#import_button").click(function() {
        AJS.dialog2("#import_dialog").show();
    });

    $("#import_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#import_dialog").hide();
    });

    $("#import_dialog_submit_button").click(function() {
        var fileData = $('#import_file').prop('files')[0];
        var formData = new FormData();
        formData.append('file', fileData);
        $.ajax({
            url: apiUrlPrefix + "projects/import",
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
    $("#export_button").click(function() {
        AJS.dialog2("#export_dialog").show();
    });

    $("#export_dialog_close_button").click(function(e) {
        e.preventDefault();
        AJS.dialog2("#export_dialog").hide();
    });

    $("#export_dialog_submit_button").click(function() {
        $.ajax({
            url: apiUrlPrefix + "projects/1/export",
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
    app.ProjectsView = Backbone.View.extend({
        el: "#projects",

        initialize: function(){
            var self = this;
            app.projectFolders.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function(){
            var result = "";
            app.projectFolders.each(function(folder) {
                result += app.FolderTemplate({folder:folder});
            });
            this.$el.html(result);
        }
    });

    app.projectsView = new app.ProjectsView();
}

function initRequirements() {
    app.RequirementsView = Backbone.View.extend({
        el: "#requirements",

        initialize: function(){
            var self = this;
            app.requirements.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function(){
            var result = "";
            app.requirements.each(function(requirement) {
                result += app.RequirementTemplate({requirement:requirement});
            });
            this.$el.html(result);
        }
    });

    app.requirementsView = new app.RequirementsView();
}