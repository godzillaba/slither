"""
    Module printing summary of interfaces and their pragma versions
"""
from slither.printers.abstract_printer import AbstractPrinter
from slither.utils.myprettytable import MyPrettyTable


class InterfaceFinder(AbstractPrinter):

    ARGUMENT = "interface-finder"
    HELP = "Finds interfaces and their supported compiler version range"

    WIKI = "https://github.com/trailofbits/slither/wiki/Printer-documentation#interface-finder"

    def output(self, _filename):
        """
        _filename is not used
        Args:
            _filename(string)
        """

        txt = ""
        all_tables = []
        
        # Find all interfaces across all compilation units
        interfaces_found = []
        
        for compilation_unit in self.slither.compilation_units:
            # Find all interfaces in this compilation unit
            for contract in compilation_unit.contracts:
                if contract.is_interface:
                    # Get pragma versions specifically from the interface's file
                    interface_file = contract.source_mapping.filename if contract.source_mapping else None
                    
                    # Skip interfaces from node_modules
                    if interface_file and "node_modules" in str(interface_file):
                        continue
                        
                    pragma_versions = []
                    
                    if interface_file:
                        # Get pragma directives from the file scope that contains this interface
                        file_scope = contract.file_scope
                        for pragma in compilation_unit.pragma_directives:
                            if pragma.is_solidity_version and pragma.scope == file_scope:
                                pragma_versions.append(pragma.version)
                    
                    # Convert pragma versions to a readable format
                    if pragma_versions:
                        version_range = ", ".join(set(pragma_versions))  # Remove duplicates
                    else:
                        version_range = "No version specified"
                    
                    # Use relative path for cleaner display
                    file_display = interface_file.relative if interface_file else "Unknown"
                    
                    interfaces_found.append({
                        'name': contract.name,
                        'version_range': version_range,
                        'file': str(file_display)
                    })
        
        if not interfaces_found:
            txt += "No interfaces found in the project.\n"
        else:
            txt += f"Found {len(interfaces_found)} interface(s):\n\n"
            
            # Create a table for all interfaces
            table = MyPrettyTable(["Interface Name", "File", "Pragma Version"])
            
            for interface in interfaces_found:
                table.add_row([
                    interface['name'],
                    interface['file'],
                    interface['version_range']
                ])
            
            txt += str(table) + "\n"
            all_tables.append(("Interfaces", table))
        
        self.info(txt)
        
        res = self.generate_output(txt)
        for name, table in all_tables:
            res.add_pretty_table(table, name)
        
        return res