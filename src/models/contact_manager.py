"""
Contact Manager - Handles operations on contacts
"""
from typing import List, Dict, Any, Optional, Tuple
import csv
import io
import phonenumbers

from src.models.database import Database

class ContactManager:
    """Manages contact operations"""
    
    def __init__(self, database: Database):
        """Initialize with a database connection"""
        self.db = database
    
    def add_contact(self, name: str, phone: str, country_code: str, notes: str = "") -> bool:
        """Add a new contact or update an existing one"""
        # Validate the phone number format
        valid, formatted = self._validate_phone_number(phone, country_code)
        if not valid:
            return False
            
        return self.db.save_contact(name, formatted, country_code, notes)
    
    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts"""
        contacts = self.db.get_contacts()
        return [dict(contact) for contact in contacts]
    
    def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Get a contact by ID"""
        contact = self.db.get_contact(contact_id)
        return dict(contact) if contact else None
    
    def update_contact(self, contact_id: int, name: Optional[str] = None, 
                      phone: Optional[str] = None, country_code: Optional[str] = None,
                      notes: Optional[str] = None) -> bool:
        """Update a contact"""
        # Get current contact
        current = self.db.get_contact(contact_id)
        if not current:
            return False
            
        # Use current values if not provided
        name = name if name is not None else current['name']
        phone = phone if phone is not None else current['phone']
        country_code = country_code if country_code is not None else current['country_code']
        notes = notes if notes is not None else current['notes']
        
        # Validate phone number if changed
        if phone != current['phone'] or country_code != current['country_code']:
            valid, formatted = self._validate_phone_number(phone, country_code)
            if not valid:
                return False
            phone = formatted
            
        return self.db.save_contact(name, phone, country_code, notes)
    
    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact"""
        return self.db.delete_contact(contact_id)
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search contacts by name or phone number"""
        contacts = self.db.search_contacts(query)
        return [dict(contact) for contact in contacts]
    
    def import_contacts_from_csv(self, csv_data: str) -> Tuple[int, List[str]]:
        """Import contacts from CSV data"""
        success_count = 0
        errors = []
        
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        
        required_fields = ['name', 'phone']
        
        # Check if required fields are present
        fieldnames = reader.fieldnames
        if not fieldnames:
            return 0, ["Invalid CSV format: No header row found"]
            
        for field in required_fields:
            if field not in fieldnames:
                return 0, [f"Required field '{field}' missing from CSV"]
        
        # Process contacts
        line_num = 1  # Skip header row in count
        for row in reader:
            line_num += 1
            name = row.get('name', '').strip()
            phone = row.get('phone', '').strip()
            country_code = row.get('country_code', '').strip()
            notes = row.get('notes', '').strip()
            
            # Skip empty rows
            if not name and not phone:
                continue
                
            # Validate required fields
            if not name:
                errors.append(f"Line {line_num}: Name is required")
                continue
                
            if not phone:
                errors.append(f"Line {line_num}: Phone is required")
                continue
                
            # If country code not provided in CSV, try to extract from phone
            if not country_code:
                try:
                    parsed = phonenumbers.parse(phone, None)
                    country_code = phonenumbers.region_code_for_number(parsed)
                except:
                    country_code = "US"  # Default to US if not specified
            
            # Add the contact
            if self.add_contact(name, phone, country_code, notes):
                success_count += 1
            else:
                errors.append(f"Line {line_num}: Failed to add contact '{name}'")
        
        return success_count, errors
    
    def export_contacts_to_csv(self) -> str:
        """Export all contacts to CSV format"""
        contacts = self.get_all_contacts()
        if not contacts:
            return "name,phone,country_code,notes\n"
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['name', 'phone', 'country_code', 'notes'])
        writer.writeheader()
        
        for contact in contacts:
            writer.writerow({
                'name': contact['name'],
                'phone': contact['phone'],
                'country_code': contact['country_code'],
                'notes': contact.get('notes', '')
            })
            
        return output.getvalue()
    
    def _validate_phone_number(self, phone: str, country_code: str) -> Tuple[bool, str]:
        """Validate and format a phone number"""
        try:
            # If the phone doesn't start with +, add the country code
            if not phone.startswith('+'):
                # If the country code already has +, don't add another
                prefix = "" if country_code.startswith('+') else "+"
                # Parse with country code
                parsed = phonenumbers.parse(f"{prefix}{country_code}{phone}", None)
            else:
                # Parse as is if it has +
                parsed = phonenumbers.parse(phone, None)
                
            # Check if it's a valid number
            if not phonenumbers.is_valid_number(parsed):
                return False, ""
                
            # Format to E.164 format
            formatted = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164)
                
            return True, formatted
            
        except phonenumbers.NumberParseException:
            return False, "" 