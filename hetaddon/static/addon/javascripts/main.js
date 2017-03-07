var apiUrlPrefix = "api/";
var app = {};
var currentTab = null;

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

function addDocument(section_id) {
    $('#add_document_file_' + section_id).trigger("click");
}

function uploadDocument(element, section_id) {
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
                section_id:section_id
            };
            $.ajax({
                url: apiUrlPrefix + "documents",
                method: "POST",
                data: JSON.stringify(data),
                success: function() {
                    showSuccessMessage("The Document was uploaded successfully");
                    refreshSections();
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
                refreshSections();
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
        project_id:currentTab.get("project_id")
    };
    $.ajax({
        url: apiUrlPrefix + "sections",
        method: "POST",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Section was created successfully");
            refreshSections();
        },
        error: function() {
            showErrorMessage("The section could not be created, please try again or contact our webmaster.");
        }
    });
}

function updateSection(id) {
    var data = {
        name:document.getElementById("section_" + id + "_name").value
    };
    $.ajax({
        url: apiUrlPrefix + "sections/" + id,
        method: "PUT",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Section was updated successfully");
            refreshSections();
        },
        error: function() {
            showErrorMessage("The section could not be updated, please try again or contact our webmaster.");
        }
    });
}

function rejectValue(id) {
    var data = {
        rejected:true
    };
    $.ajax({
        url: apiUrlPrefix + "values/" + id,
        method: "PUT",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Requirement Value was rejected successfully");
            refreshRequirements();
        },
        error: function() {
            showErrorMessage("The requirement value could not be rejected, please try again or contact our webmaster.");
        }
    });
}

function disableValue(id) {
    var data = {
        disabled:true
    };
    $.ajax({
        url: apiUrlPrefix + "values/" + id,
        method: "PUT",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Requirement Value was disabled successfully");
            refreshRequirements();
        },
        error: function() {
            showErrorMessage("The requirement value could not be disabled, please try again or contact our webmaster.");
        }
    });
}

function addValue(requirement_id) {
    var data = {
        values_shown:app.requirements.get(requirement_id).get("values_shown") + 1
    };
    $.ajax({
        url: apiUrlPrefix + "requirements/" + requirement_id,
        method: "PUT",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Requirement was updated successfully");
            refreshRequirements();
        },
        error: function() {
            showErrorMessage("The requirement could not be updated, please try again or contact our webmaster.");
        }
    });
}

function removeValue(requirement_id) {
    values_shown = app.requirements.get(requirement_id).get("values_shown") - 1;
    if (values_shown == 0) values_shown = 1;
    var data = {
        values_shown: values_shown
    };
    $.ajax({
        url: apiUrlPrefix + "requirements/" + requirement_id,
        method: "PUT",
        data: JSON.stringify(data),
        success: function() {
            showSuccessMessage("The Requirement was updated successfully");
            refreshRequirements();
        },
        error: function() {
            showErrorMessage("The requirement could not be updated, please try again or contact our webmaster.");
        }
    });
}

function runAnalysis() {
    app.waitingDialog.show("Extraction running");
    $.ajax({
        url: apiUrlPrefix + "projects/" + currentTab.get("project_id") + "/analyze",
        method: "POST",
        success: function() {
            showSuccessMessage("The analysis was successful.");
            refreshRequirements();
            refreshProjectFolders();
            app.waitingDialog.hide();
        },
        error: function() {
            showErrorMessage("The analysis could not be carried out, please try again or contact our webmaster.");
            app.waitingDialog.hide();
        }
    });
}

function importProject() {

}

function exportProject() {
    
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

function refreshSections() {
    console.log("Synchronizing Sections");
    app.sections.fetch({reset: true});
}

function refreshProjectFolders() {
    console.log("Synchronizing Folders and Projects");
    app.projectFolders.fetch({reset: true});
}

function refreshRequirements() {
    console.log("Synchronizing Requirements");
    app.requirements.fetch({reset: true}).done(function() {
        $("textarea").each(function(index, element) {
            element.style.height = element.scrollHeight + "px";
        });
    });
}

function refreshAll(){
    refreshProjectFolders();
    if(currentTab != null) {
        refreshSections();
        refreshRequirements();
    }
}

function showTab(project_id, type) {
    var typeEnumValue = app.TabTypeEnum[type]
    var tabData = {project_id: project_id, type: typeEnumValue};
    var tabsFound = app.openedTabs.where(tabData);
    if(tabsFound.length > 1) throw "Invalid tab collection";
    if(tabsFound.length == 1) {
        currentTab = tabsFound[0];
    } else {
        var project = app.projectFolders.getProject(project_id);
        tabData.project_name = project.get("name");
        currentTab = new app.Tab(tabData);
        app.openedTabs.add(currentTab);
    }

    refreshSections();
    refreshRequirements();

    app.tabsView.render();

    var documentsTab = $("#tab_documents");
    var requirementsTab = $("#tab_requirements");
    var activeClass = "active-pane";
    switch (typeEnumValue) {
        case app.TabTypeEnum.DOCUMENTS:
            documentsTab.addClass(activeClass);
            requirementsTab.removeClass(activeClass);
            break;
        case app.TabTypeEnum.REQUIREMENTS:
            documentsTab.removeClass(activeClass);
            requirementsTab.addClass(activeClass);
            break;
        default:
            throw "Not implemented enum value";
    }
}

function closeTab(project_id, type) {

}

(function() {
    $.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });

    initModels();
    initTemplates();
    initCollectionInstances();
    initTabs();
    initSections();
    initProjects();
    initFolderList();
    initRequirements();
    initNewProjectDialog();
    initNewFolderDialog();
    initImportDialog();
    initExportDialog();
    initRunAnalysis();
    initWaitingDialog();

    if(IN_IFRAME) {
        loadConnectScript();
        setUserKey(function () {
            refreshAll();
            setInterval(refreshAll,30000);
        });
    }else{
        refreshAll();
        setInterval(refreshAll,30000);
    }

})();

function loadConnectScript() {
    var getUrlParam = function (param) {
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

    document.getElementsByTagName("head")[0].appendChild(script);
}

function setUserKey(done) {
    if (typeof AP !== 'undefined') {
        AP.getUser(function(user) {
            console.log("Retrieved user id:" + user.id + "user key:" + user.key + ", user name:" + user.fullName);
            app.User = {key: user.key, fullName: user.fullName};
            return done();
        });
    } else {
        console.log("AP is not initialized. Will try again in 2s.");
        setTimeout(function() {
            setUserKey(done)
        }, 2000);
    }
}

function initModels() {
    app.TabTypeEnum = {
        DOCUMENTS: {
            value: "DOCUMENTS",
            toString: function() {return "Documents"}
        },
        REQUIREMENTS: {
            value: "REQUIREMENTS",
            toString: function() {return "Requirements"}
        }
    };

    app.Tab = Backbone.Model.extend({
        defaults: {
            project_id: 0,
            project_name: "",
            type: app.TabTypeEnum.DOCUMENTS.value
        }
    });

    app.TabList = Backbone.Collection.extend({
        model: app.Tab
    });

    app.Section = Backbone.Model.extend({
        initialize: function() {
            var documents = this.get("documents");
            if (!Array.isArray(documents)) {
                documents = [];
            }
            this.set({documents: new app.DocumentList(documents)});
        },

        defaults: {
            id: 0,
            name: ""
        },
        url: apiUrlPrefix + "sections"
    });

    app.SectionList = Backbone.Collection.extend({
        model: app.Section,
        url: function() {
            return apiUrlPrefix + "projects/" + currentTab.get("project_id") + "/sections";
        }
    });

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
        model: app.Document
    });

    app.Project = Backbone.Model.extend({
        defaults: {
            id: 0,
            name: "",
            requirements_extracted: false
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
        url: apiUrlPrefix + "folders",

        getProject: function(project_id) {
            var matchingProject = this.get("projects").get(project_id);
            if (matchingProject != null) return matchingProject;

            return this.get("folders").getProject(project_id);
        }
    });

    app.FolderList = Backbone.Collection.extend({
        model: app.Folder,
        url: apiUrlPrefix + "folders",

        getProject: function(project_id) {
            for(var i = 0; i < this.models.length; i++) {
                var project = this.models[i].getProject(project_id);
                if(project != null) return project;
            }
            return null;
        }
    });

    app.RequirementValue = Backbone.Model.extend({
        defaults: {
            id: 0,
            data: "",
            disabled: false,
            document_id: 0
        },
        url: apiUrlPrefix + "values"
    });

    app.RequirementValueList = Backbone.Collection.extend({
        model: app.RequirementValue
    });

    app.Requirement = Backbone.Model.extend({
        initialize: function() {
            var values = this.get("values");
            if (!Array.isArray(values)) {
                values = [];
            }
            this.set({values: new app.RequirementValueList(values)});
        },

        defaults: {
            name: "",
            values_shown: 1
        },
        url: apiUrlPrefix + "requirements"
    });

    app.RequirementList = Backbone.Collection.extend({
        model: app.Requirement,
        url: function() {
            return apiUrlPrefix + "projects/" + currentTab.get("project_id") + "/requirements";
        }
    });
}

function initTemplates() {
    app.TabButtonTemplate = _.template($("#tab_button_template").html());
    app.SectionTemplate = _.template($("#section_template").html());
    app.DocumentRowTemplate = _.template($("#document_row_template").html());
    app.FolderOptionTemplate = _.template($("#folder_option_template").html());
    app.FolderTemplate = _.template($("#folder_template").html());
    app.ProjectTemplate = _.template($("#project_template").html());
    app.RequirementTemplate = _.template($("#requirement_template").html());
}

function initCollectionInstances() {
    app.sections = new app.SectionList();
    app.projectFolders = new app.FolderList();
    app.requirements = new app.RequirementList();
    app.openedTabs = new app.TabList();
}

function initTabs() {
    app.TabsView = Backbone.View.extend({
        el: "#tab_buttons",

        initialize: function() {
            var self = this;
            app.openedTabs.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function() {
            var result = "";
            app.openedTabs.each(function(tab) {
                result += app.TabButtonTemplate({tab: tab, active: currentTab == tab});
            });
            this.$el.html(result);
        }
    });

    app.tabsView = new app.TabsView();
}

function initSections() {
    app.SectionsView = Backbone.View.extend({
        el: "#sections",

        initialize: function() {
            var self = this;
            app.sections.bind("reset", _.bind(self.render, self));
            self.render();
        },

        render: function() {
            var result = "";
            app.sections.each(function(section) {
                result += app.SectionTemplate({section: section});
            });
            this.$el.html(result);
        }
    });

    app.sectionsView = new app.SectionsView();
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
            url: apiUrlPrefix + "projects/" + currentTab.get("project_id") + "/export",
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

function initWaitingDialog() {
    app.waitingDialog = (function ($) {
        'use strict';

        // Creating modal dialog's DOM
        var $dialog = $(
            '<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
            '<div class="modal-dialog modal-m">' +
            '<div class="modal-content">' +
                '<div class="modal-header"><h3 style="margin:0;"></h3></div>' +
                '<div class="modal-body">' +
                    '<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%"></div></div>' +
                '</div>' +
            '</div></div></div>');

        return {
            /**
             * Opens our dialog
             * @param message Custom message
             * @param options Custom options:
             * 				  options.dialogSize - bootstrap postfix for dialog size, e.g. "sm", "m";
             * 				  options.progressType - bootstrap postfix for progress bar type, e.g. "success", "warning".
             */
            show: function (message, options) {
                // Assigning defaults
                if (typeof options === 'undefined') {
                    options = {};
                }
                if (typeof message === 'undefined') {
                    message = 'Loading';
                }
                var settings = $.extend({
                    dialogSize: 'm',
                    progressType: '',
                    onHide: null // This callback runs after the dialog was hidden
                }, options);

                // Configuring dialog
                $dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-' + settings.dialogSize);
                $dialog.find('.progress-bar').attr('class', 'progress-bar');
                if (settings.progressType) {
                    $dialog.find('.progress-bar').addClass('progress-bar-' + settings.progressType);
                }
                $dialog.find('h3').text(message);
                // Adding callbacks
                if (typeof settings.onHide === 'function') {
                    $dialog.off('hidden.bs.modal').on('hidden.bs.modal', function (e) {
                        settings.onHide.call($dialog);
                    });
                }
                // Opening dialog
                $dialog.modal();
            },
            /**
             * Closes dialog
             */
            hide: function () {
                $dialog.modal('hide');
            }
        };

    })(jQuery);
}