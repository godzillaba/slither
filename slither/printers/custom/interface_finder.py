"""
    Module printing summary of interfaces and their pragma versions
"""
from slither.printers.abstract_printer import AbstractPrinter
from slither.utils.myprettytable import MyPrettyTable


class InterfaceFinder(AbstractPrinter):

    ARGUMENT = "interface-finder"
    HELP = "Finds interfaces and their supported compiler version range"

    WIKI = "https://github.com/trailofbits/slither/wiki/Printer-documentation#interface-finder"

    def _get_pragma_version_for_item(self, item, compilation_unit):
        """Helper function to get pragma version for any item (interface, enum, struct, event)"""
        item_file = item.source_mapping.filename if item.source_mapping else None
        
        # Skip items from node_modules
        if item_file and "node_modules" in str(item_file):
            return None, None
            
        pragma_versions = []
        
        if item_file:
            # Get pragma directives from the file scope that contains this item
            file_scope = item.file_scope
            for pragma in compilation_unit.pragma_directives:
                if pragma.is_solidity_version and pragma.scope == file_scope:
                    pragma_versions.append(pragma.version)
        
        # Convert pragma versions to a readable format
        if pragma_versions:
            version_range = ", ".join(set(pragma_versions))  # Remove duplicates
        else:
            version_range = "No version specified"
        
        # Use relative path for cleaner display
        file_display = item_file.relative if item_file else "Unknown"
        
        return version_range, str(file_display)

    def _process_items(self, item_type, items, compilation_unit, items_found):
        """Helper function to process a collection of items of a specific type"""
        for item in items:
            version_range, file_display = self._get_pragma_version_for_item(item, compilation_unit)
            if version_range is not None:  # Skip if from node_modules
                items_found.append({
                    'name': item.name,
                    'type': item_type,
                    'version_range': version_range,
                    'file': file_display
                })

    def output(self, _filename):
        """
        _filename is not used
        Args:
            _filename(string)
        """

        txt = ""
        all_tables = []
        
        # Find all interfaces, top-level enums, and structs across all compilation units
        items_found = []
        
        for compilation_unit in self.slither.compilation_units:
            # Process contracts
            contracts = [c for c in compilation_unit.contracts if not c.is_interface]
            self._process_items('Contract', contracts, compilation_unit, items_found)

            # Process interfaces
            interfaces = [c for c in compilation_unit.contracts if c.is_interface]
            self._process_items('Interface', interfaces, compilation_unit, items_found)

            # Process libraries
            libraries = [c for c in compilation_unit.contracts if c.is_library]
            self._process_items('Library', libraries, compilation_unit, items_found)
            
            # Process top-level enums
            self._process_items('Enum', compilation_unit.enums_top_level, compilation_unit, items_found)
            
            # Process top-level structs
            self._process_items('Struct', compilation_unit.structures_top_level, compilation_unit, items_found)
            
            # Process top-level events
            self._process_items('Event', compilation_unit.events_top_level, compilation_unit, items_found)

            # Process top-level errors
            self._process_items('Error', compilation_unit.custom_errors, compilation_unit, items_found)
        
        if not items_found:
            txt += "No interfaces, top-level enums, structs, or events found in the project.\n"
        else:
            txt += f"Found {len(items_found)} item(s):\n\n"
            
            # Create a table for all items
            table = MyPrettyTable(["Name", "Type", "File", "Pragma Version"])
            
            for item in items_found:
                table.add_row([
                    item['name'],
                    item['type'],
                    item['file'],
                    item['version_range']
                ])
            
            txt += str(table) + "\n"
            all_tables.append(("Interfaces, Enums, Structs & Events", table))
        
        self.info(txt)
        
        res = self.generate_output(txt)
        for name, table in all_tables:
            res.add_pretty_table(table, name)
        
        return res