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
        """Helper function to get pragma version for any item (interface, enum, struct)"""
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
            # Find all interfaces in this compilation unit
            for contract in compilation_unit.contracts:
                if contract.is_interface:
                    version_range, file_display = self._get_pragma_version_for_item(contract, compilation_unit)
                    if version_range is not None:  # Skip if from node_modules
                        items_found.append({
                            'name': contract.name,
                            'type': 'Interface',
                            'version_range': version_range,
                            'file': file_display
                        })
            
            # Find all top-level enums
            for enum in compilation_unit.enums_top_level:
                version_range, file_display = self._get_pragma_version_for_item(enum, compilation_unit)
                if version_range is not None:  # Skip if from node_modules
                    items_found.append({
                        'name': enum.name,
                        'type': 'Enum',
                        'version_range': version_range,
                        'file': file_display
                    })
            
            # Find all top-level structs
            for struct in compilation_unit.structures_top_level:
                version_range, file_display = self._get_pragma_version_for_item(struct, compilation_unit)
                if version_range is not None:  # Skip if from node_modules
                    items_found.append({
                        'name': struct.name,
                        'type': 'Struct',
                        'version_range': version_range,
                        'file': file_display
                    })
        
        if not items_found:
            txt += "No interfaces, top-level enums, or structs found in the project.\n"
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
            all_tables.append(("Interfaces, Enums & Structs", table))
        
        self.info(txt)
        
        res = self.generate_output(txt)
        for name, table in all_tables:
            res.add_pretty_table(table, name)
        
        return res