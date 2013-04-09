"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

App that creates folders on disk from inside of Shotgun.

"""

from tank.platform import Application
import tank

class CreateFolders(Application):
    
    def init_app(self):
        # Clone the list because we may modify it
        entity_types = list(self.get_setting("entity_types"))
        deny_permissions = self.get_setting("deny_permissions")
        deny_platforms = self.get_setting("deny_platforms")
                
        p = {
            "title": "Create Folders",
            "entity_types": entity_types,
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }
        
        self.engine.register_command("create_folders", self.create_folders, p)

        p = {
            "title": "Preview Create Folders",
            "entity_types": entity_types,
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }
        
        self.engine.register_command("preview_folders", self.preview_create_folders, p)

    
    def _add_plural(self, word, items):
        """
        appends an s if items > 1
        """
        if items > 1:
            return "%ss" % word
        else:
            return word

    def preview_create_folders(self, entity_type, entity_ids):
        
        if len(entity_ids) == 0:
            self.log_info("No entities specified!")
            return
        
        #################################################################################
        #
        # Add the project (assume all entities belong to the same project)
        # the reason we need the project is to make sure that any static child folders
        # on the project level are properly created. This is because you run actions 
        # from the shotgun project entities.
        #
        if entity_type != "Project":
            data = self.shotgun.find_one(entity_type, [["id", "is", entity_ids[0]]], ["project"])
            project_id = data["project"]["id"]
        
        paths = []
        try:
            paths.extend( self.tank.preview_filesystem_structure(entity_type, entity_ids) )
        except tank.TankError, tank_error:
            # tank errors are errors that are expected and intended for the user
            self.log_error(tank_error)
        except Exception, error:
            # other errors are not expected and probably bugs - here it's useful with a callstack.
            self.log_exception("Error when previewing folders!")
        
        # report back to user
        if len(paths) == 0:
            self.log_info("<b>No folders would be generated on disk for this item!</b>")

        else:
            self.log_info("<b>Creating folders would generate %d items on disk:</b>" % len(paths))
            self.log_info("")
            for p in paths:
                self.log_info(p)
                

    def create_folders(self, entity_type, entity_ids):
        
        if len(entity_ids) == 0:
            self.log_info("No entities specified!")
            return
        
        entities_processed = 0
        try:
            entities_processed = self.tank.create_filesystem_structure(entity_type, entity_ids)
        except tank.TankError, tank_error:
            # tank errors are errors that are expected and intended for the user
            self.log_error(tank_error)

        except Exception, error:
            # other errors are not expected and probably bugs - here it's useful with a callstack.
            self.log_exception("Error when creating folders!")
        
        # report back to user
        self.log_info("%d %s processed - "
                     "Processed %d folders on disk." % (len(entity_ids), 
                                                        self._add_plural(entity_type, len(entity_ids)), 
                                                        entities_processed))            
        
    
        
        
