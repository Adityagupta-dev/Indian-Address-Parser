import random
from faker import Faker
import json

class IndianAddressGenerator:
    def __init__(self):
        self.fake = Faker('en_IN')
        
        self.prefix_types = ['Flat', 'Shop', 'Plot', 'Unit', 'Office', 'Room', 'House']
        self.building_types = ['Apartments', 'Towers', 'Heights', 'Complex', 'Residency', 'Plaza', 'Manor', 
                             'Building', 'Society', 'Enclave', 'Paradise', 'Arcade', 'Hub', 'Empire']
        self.landmarks = ['near', 'opposite', 'behind', 'next to', 'adjacent to', 'in front of']
        self.landmark_places = ['Railway Station', 'Metro Station', 'Bus Stop', 'Hospital', 'Mall', 'Park',
                              'Temple', 'School', 'Market', 'Police Station', 'Bank', 'Restaurant']
        self.areas = ['Sector', 'Colony', 'Nagar', 'Layout', 'Extension', 'Phase', 'Block', 'Area', 
                     'Industrial Area', 'Business Park', 'Township']
        self.streets = ['Road', 'Street', 'Lane', 'Marg', 'Path', 'Avenue', 'Boulevard']

        # Common email/document contexts
        self.contexts = [
            "Delivery Address: {address}",
            "Please deliver to: {address}",
            "My new address is {address}",
            "The meeting will be held at {address}",
            "Our office has moved to {address}",
            "The event venue is {address}",
            "For correspondence: {address}",
            "Please update my address to {address}",
            "The pickup location is {address}",
            "{name}'s residence: {address}",
            "The property is located at {address}",
            "Send all documents to {address}",
            "Current residence: {address}",
            "Billing Address: {address}",
            "Site Location: {address}",
            "Letterhead: {name}\n{designation}\n{institute}\n{address}\n{contact_info}"
        ]

    def generate_unit_number(self):
        """Generate random unit number in various formats"""
        formats = [
            f"{random.choice(self.prefix_types)} No. {random.randint(1, 999)}",
            f"{random.choice(self.prefix_types)} {random.randint(1, 999)}",
            f"#{random.randint(1, 999)}",
            f"{random.randint(1, 999)}/{random.randint(1, 100)}",
            f"{random.choice(self.prefix_types)}-{random.randint(1, 999)}"
        ]
        return random.choice(formats)

    def generate_building_name(self):
        """Generate random building name"""
        formats = [
            f"{self.fake.last_name()} {random.choice(self.building_types)}",
            f"{self.fake.first_name()} {random.choice(self.building_types)}",
            f"{random.choice(['The', 'Sri', 'Shree', ''])} {self.fake.last_name()} {random.choice(self.building_types)}",
            f"{self.fake.company()} {random.choice(self.building_types)}"
        ]
        return random.choice(formats)

    def generate_landmark(self):
        """Generate random landmark"""
        return f"{random.choice(self.landmarks)} {random.choice(self.landmark_places)}"

    def generate_street(self):
        """Generate random street name"""
        formats = [
            f"{self.fake.street_name()} {random.choice(self.streets)}",
            f"{random.randint(1, 100)}th {random.choice(self.streets)}",
            f"Main {random.choice(self.streets)}",
            f"Cross {random.choice(self.streets)} {random.randint(1, 20)}"
        ]
        return random.choice(formats)

    def generate_area(self):
        """Generate random area name"""
        formats = [
            f"{random.choice(self.areas)} {random.randint(1, 100)}",
            f"{self.fake.city()}-{random.choice(['E', 'W', 'N', 'S'])}"
        ]
        return random.choice(formats)

    def generate_pincode(self, city):
        """Generate pincode in various formats"""
        pincode = self.fake.postcode()
        formats = [
            f"{pincode}",
            f"{city}-{pincode}",
            f"{city} {pincode}",
            f"PIN: {pincode}",
            f"Pincode: {pincode}",
            f"{city}-{random.randint(1, 99)}"
        ]
        return random.choice(formats)

    def generate_single_address(self):
        """Generate single address with variations"""
        city = self.fake.city()
        state = self.fake.state()
        
        # Randomly decide which components to include
        has_unit = random.random() < 0.9
        has_building = random.random() < 0.95
        has_landmark = random.random() < 0.7
        has_street = random.random() < 0.9
        has_area = random.random() < 0.8
        include_india = random.random() < 0.5
        
        # Build address components
        components = {}
        address_parts = []
        
        if has_unit:
            unit = self.generate_unit_number()
            components['room_no'] = unit
            address_parts.append(unit)
        
        if has_building:
            building = self.generate_building_name()
            components['building_name'] = building
            address_parts.append(building)
            
        if has_landmark:
            landmark = self.generate_landmark()
            components['landmark'] = landmark
            address_parts.append(landmark)
            
        if has_street:
            street = self.generate_street()
            components['street'] = street
            address_parts.append(street)
            
        if has_area:
            area = self.generate_area()
            components['area'] = area
            address_parts.append(area)
            
        components['city'] = city
        address_parts.append(city)
        
        components['state'] = state
        address_parts.append(state)
        
        pincode = self.generate_pincode(city)
        components['pincode'] = pincode
        address_parts.append(pincode)
        
        if include_india:
            address_parts.append("India")
        
        # Join address parts with random separators
        separators = [', ', ' ', ', ', ' - ', ', ']
        address = ''
        for i, part in enumerate(address_parts):
            if i > 0:
                address += random.choice(separators)
            address += part
            
        # Add context
        context = random.choice(self.contexts)
        full_text = context.format(
            address=address,
            name=self.fake.name(),
            designation=self.fake.job(),
            institute=self.fake.company(),
            contact_info=f"Email: {self.fake.email()}, Phone: {self.fake.phone_number()}"
        )
        
        return {
            "text": full_text,
            "annotations": components
        }

    def generate_dataset(self, num_samples=5000, output_file="address_dataset.json"):
        """Generate multiple addresses and save to file"""
        addresses = [self.generate_single_address() for _ in range(num_samples)]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(addresses, f, indent=2, ensure_ascii=False)
        
        return addresses

if __name__ == "__main__":
    generator = IndianAddressGenerator()
    addresses = generator.generate_dataset(5000)
    print(f"Generated {len(addresses)} addresses")
    print("\nSample addresses:")
    for i in range(3):
        print(f"\n{i+1}. {addresses[i]['text']}")
