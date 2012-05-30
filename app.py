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
        
        if "Task" in entity_types:
            task_idx = entity_types.index("Task")
            del entity_types[task_idx]
            
            p = {
                "title": "Create Folders for Associated Entity",
                "entity_types": ["Task"],
                "deny_permissions": deny_permissions,
                "deny_platforms": deny_platforms,
                "supports_multiple_selection": True
            }

            self.engine.register_command("task_create_folders", self.create_folders, p)
        
        p = {
            "title": "Create Folders",
            "entity_types": entity_types,
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }
        
        self.engine.register_command("create_folders", self.create_folders, p)
    
    def _add_plural(self, word, items):
        """
        appends an s if items > 1
        """
        if items > 1:
            return "%ss" % word
        else:
            return word

    def create_folders(self, entity_type, entity_ids):
        entities_processed = 0
        try:
            entities_processed = self.tank.create_filesystem_structure(entity_type, entity_ids)
        except tank.TankError, tank_error:
            # tank errors are errors that are expected and intended for the user
            self.engine.log_error(tank_error)

        except Exception as error:
            # other errors are not expected and probably bugs - here it's useful with a callstack.
            self.engine.log_exception("Error when creating folders!")
        
        # report back to user
        if entities_processed < 2: # project always processed
            if entity_type == "Task":
                self.engine.log_info("No folders processed!")
                
            else:
                self.engine.log_info("No folders processed - there is no folder configuration "
                                     "for %s entities!" % entity_type)
        
        else:
            if entity_type == "Task":
                self.engine.log_info("%d %s processed - "
                                     "Processed a total of %d Entities, "
                                     "Steps and Tasks." % (len(entity_ids), 
                                                           self._add_plural(entity_type, len(entity_ids)), 
                                                           entities_processed))            
            else:
                self.engine.log_info("%d %s processed - "
                                     "Processed a total of %d %s, "
                                     "Steps and Tasks." % (len(entity_ids), 
                                                           self._add_plural(entity_type, len(entity_ids)), 
                                                           entities_processed, 
                                                           self._add_plural(entity_type, 2)))
        
    
        
        
