from gedcom.parser import Parser
# from gedcom.writer import GedcomWriter
# from gedcom.tags import Tag

class Gedcom:
    def __init__(self, filepath):
        self.filepath = filepath
        self.individuals = []
        self.root_element = None
        self._parse_gedcom()

    @staticmethod
    def create_empty_gedcom(filepath):
        with open(filepath, 'w') as f:
            f.write("0 HEAD\n")
            f.write("1 CHAR UTF-8\n")
            f.write("1 GEDC\n")
            f.write("2 VERS 5.5.1\n")
            f.write("1 SUBM @SUBM@\n")
            f.write("0 @SUBM@ SUBM\n")
            f.write("1 NAME Unknown\n")
            f.write("0 TRLR\n")

    def _parse_gedcom(self):
        parser = Parser()
        parser.parse_file(self.filepath)
        
        self.root_element = parser.get_root_element()
        for element in self.root_element.get_child_elements():
            if element.get_tag() == 'INDI':
                self.individuals.append(Individual(element))

    def get_individual_by_id(self, individual_id):
        for individual in self.individuals:
            if individual.id == individual_id:
                return individual
        return None

    def update_individual(self, individual_id, new_name, new_birth_date, new_birth_place):
        individual = self.get_individual_by_id(individual_id)
        if individual:
            old_name = individual.name
            old_birth_date = individual.birth_date
            old_birth_place = individual.birth_place

            individual.name = new_name
            individual.birth_date = new_birth_date
            individual.birth_place = new_birth_place
            
            with open(self.filepath, 'r') as f:
                lines = f.readlines()
            
            updated_lines = []
            in_individual_block = False
            name_updated = False
            skip_birt_block = False
            birth_date_updated = False
            birth_place_updated = False

            for i, line in enumerate(lines):
                if line.strip() == f"0 {individual_id} INDI":
                    in_individual_block = True
                    name_updated = False
                    birth_date_updated = False
                    birth_place_updated = False
                    updated_lines.append(line)
                elif in_individual_block and line.startswith("1 NAME ") and not name_updated:
                    updated_lines.append(f"1 NAME {new_name}\n")
                    name_updated = True
                elif in_individual_block and line.startswith("1 BIRT"):
                    skip_birt_block = True
                    updated_lines.append(line)
                elif skip_birt_block and line.startswith("2 DATE ") and not birth_date_updated:
                    updated_lines.append(f"2 DATE {new_birth_date}\n")
                    birth_date_updated = True
                elif skip_birt_block and line.startswith("2 PLAC ") and not birth_place_updated:
                    updated_lines.append(f"2 PLAC {new_birth_place}\n")
                    birth_place_updated = True
                elif skip_birt_block and line.startswith("1 "):
                    skip_birt_block = False
                    updated_lines.append(line)
                elif not skip_birt_block:
                    updated_lines.append(line)

            # If no BIRT tag was found, add it after the NAME tag
            if not any("1 BIRT" in line for line in updated_lines):
                insert_index = -1
                for i, line in enumerate(updated_lines):
                    if line.startswith("1 NAME "):
                        insert_index = i + 1
                        break
                if insert_index != -1:
                    new_birt_gedcom = "1 BIRT\n"
                    if new_birth_date:
                        new_birt_gedcom += f"2 DATE {new_birth_date}\n"
                    if new_birth_place:
                        new_birt_gedcom += f"2 PLAC {new_birth_place}\n"
                    updated_lines.insert(insert_index, new_birt_gedcom)

            with open(self.filepath, 'w') as f:
                f.writelines(updated_lines)

    def save_gedcom(self, filepath):
        pass

    def add_individual(self, name, sex, birth_date='', birth_place=''):
        with open(self.filepath, 'r+') as f:
            content = f.read()
            f.seek(0) # Go to the beginning of the file
            
            # Remove TRLR and add new individual before it
            content_without_trlr = content.replace("0 TRLR\n", "")
            new_individual_id = f"@I{len(self.individuals) + 1}@"
            new_individual_gedcom = f"0 {new_individual_id} INDI\n1 NAME {name}\n1 SEX {sex}\n"
            if birth_date or birth_place:
                new_individual_gedcom += "1 BIRT\n"

                if birth_date:
                    new_individual_gedcom += f"2 DATE {birth_date}\n"
                if birth_place:
                    new_individual_gedcom += f"2 PLAC {birth_place}\n"
            
            f.write(content_without_trlr + new_individual_gedcom + "0 TRLR\n")
        
        # Re-parse the GEDCOM to update the in-memory representation
        self._parse_gedcom()

    def delete_individual(self, individual_id):
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
        
        with open(self.filepath, 'w') as f:
            skip_lines = False
            for line in lines:
                if line.strip() == f"0 {individual_id} INDI":
                    skip_lines = True
                
                if skip_lines and line.startswith("0 ") and line.strip() != f"0 {individual_id} INDI":
                    skip_lines = False
                
                if not skip_lines:
                    f.write(line)
        
        self._parse_gedcom()

    def get_families(self):
        families = []
        for element in self.root_element.get_child_elements():
            if element.get_tag() == 'FAM':
                families.append(Family(element))
        return families

class Individual:
    def __init__(self, individual_data):
        self.gedcom_element = individual_data
        self.id = individual_data.get_pointer()
        name_element = None
        birth_date_element = None
        birth_place_element = None

        for child in individual_data.get_child_elements():
            if child.get_tag() == 'NAME':
                name_element = child
            elif child.get_tag() == 'BIRT':
                for birt_child in child.get_child_elements():
                    if birt_child.get_tag() == 'DATE':
                        birth_date_element = birt_child
                    elif birt_child.get_tag() == 'PLAC':
                        birth_place_element = birt_child

        self.name = name_element.get_value() if name_element else 'Unknown'
        self.birth_date = birth_date_element.get_value() if birth_date_element else 'Unknown'
        self.birth_place = birth_place_element.get_value() if birth_place_element else 'Unknown'

class Family:
    def __init__(self, family_data):
        self.gedcom_element = family_data
        self.id = family_data.get_pointer()
        self.husband_id = None
        self.wife_id = None
        self.children_ids = []

        for child in family_data.get_child_elements():
            if child.get_tag() == 'HUSB':
                self.husband_id = child.get_value()
            elif child.get_tag() == 'WIFE':
                self.wife_id = child.get_value()
            elif child.get_tag() == 'CHIL':
                self.children_ids.append(child.get_value())