import spacy
from spacy.language import Language
from spacy.tokens import Doc
from spacy.matcher import Matcher, PhraseMatcher
from typing import List, Dict
from dataclasses import dataclass
import re
import logging
from collections import defaultdict
import fitz  # PyMuPDF
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AddressMatch:
    """Data class to store extracted address information"""
    raw_text: str
    components: Dict[str, str]
    confidence_score: float
    region: str

class IndianAddressExtractor:
    """Enhanced Indian address extraction using spaCy with comprehensive state and city data"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab)
        
        # Enhanced regional information
        self.regional_info = {
            'north_india': {
                'states': ['Delhi', 'Haryana', 'Punjab', 'Uttar Pradesh', 'Uttarakhand', 'Himachal Pradesh', 'Jammu and Kashmir', 'Leh', 'Ladakh'],
                'cities': ['Delhi', 'New Delhi', 'Gurgaon', 'Noida', 'Chandigarh', 'Lucknow', 'Kanpur', 'Varanasi', 'Prayagraj'
                          'Dehradun', 'Shimla', 'Srinagar', 'Jammu', 'Leh', 'Agra', 'Meerut', 'Ludhiana', 'Amritsar'],
                'terms': ['chowk', 'bazaar', 'gali', 'mohalla', 'nagar', 'vihar', 'kunj', 'puram']
            },
            'south_india': {
                'states': ['Karnataka', 'Tamil Nadu', 'Kerala', 'Andhra Pradesh', 'Telangana', 'Puducherry'],
                'cities': ['Bangalore', 'Chennai', 'Hyderabad', 'Kochi', 'Thiruvananthapuram', 'Mysuru', 'Coimbatore', 
                          'Madurai', 'Visakhapatnam', 'Vijayawada', 'Mangalore', 'Kozhikode', 'Thrissur', 'Warangal'],
                'terms': ['main', 'cross', 'circle', 'nilaya', 'halli', 'nagar', 'colony', 'layout']
            },
            'west_india': {
                'states': ['Maharashtra', 'Gujarat', 'Goa', 'Rajasthan'],
                'cities': ['Mumbai', 'Pune', 'Ahmedabad', 'Vadodara', 'Panaji', 'Jaipur', 'Nagpur', 'Nashik', 
                          'Surat', 'Rajkot', 'Margao', 'Jodhpur', 'Udaipur', 'Thane', 'Navi Mumbai', 'Borivali'],
                'terms': ['society', 'pada', 'wadi', 'chawl', 'villa', 'apartment', 'heights', 'towers']
            },
            'east_india': {
                'states': ['West Bengal', 'Odisha', 'Bihar', 'Assam', 'Sikkim', 'Meghalaya', 'Tripura', 
                          'Manipur', 'Nagaland', 'Arunachal Pradesh', 'Mizoram'],
                'cities': ['Kolkata', 'Bhubaneswar', 'Patna', 'Guwahati', 'Gangtok', 'Shillong', 'Agartala', 
                          'Imphal', 'Kohima', 'Itanagar', 'Aizawl', 'Cuttack', 'Siliguri'],
                'terms': ['para', 'sarani', 'bagan', 'ghat', 'tola', 'chowk', 'path', 'lane']
            }
        }
        
        self.address_markers = [
            "registered office", "corporate office", "branch office", "head office",
            "regional office", "manufacturing unit", "plant", "warehouse", "godown",
            "for correspondence", "residing at", "located at", "situated at",
            "address:", "office:", "residence:", "unit:", "plot no", "door no",
            "having its office at", "r/o", "s/o", "d/o", "w/o", "c/o",
            "limited", "ltd", "towers", "plaza", "highway", "department", "division",
            "mail stop", "floor", "building", "complex", "centre", "center",
            "landmark", "near", "beside", "opposite", "adjacent to",
            "next to", "behind", "front of", "above", "below", "cross", "junction",
            "gali", "marg", "nagar", "colony", "society", "chowk", "road no"
]
        
        self._load_address_components()
        self._add_address_patterns()
    
    def _load_address_components(self):
        """Load enhanced address components and patterns"""
        self.pin_pattern = r'\b\d{6}\b'  # Indian PIN Code (6 digits)
        self.zip_pattern = r'\b\d{5}(-\d{4})?\b'  # US ZIP code pattern

        self.states = {
            "Maharashtra": ["Maharashtra", "MH", "Maha"],
            "Delhi": ["Delhi", "New Delhi", "NCR", "DL", "National Capital Territory"],
            "Karnataka": ["Karnataka", "KA", "Kar"],
            "Tamil Nadu": ["Tamil Nadu", "Tamilnadu", "TN"],
            "West Bengal": ["West Bengal", "WB", "Bengal"],
            "Uttar Pradesh": ["Uttar Pradesh", "UP", "U.P.", "Purvanchal"],
            "Gujarat": ["Gujarat", "GJ"],
            "Rajasthan": ["Rajasthan", "RJ"],
            "Madhya Pradesh": ["Madhya Pradesh", "MP", "M.P."],
            "Andhra Pradesh": ["Andhra Pradesh", "AP"],
            "Telangana": ["Telangana", "TG", "TS"],
            "Bihar": ["Bihar", "BR"],
            "Punjab": ["Punjab", "PB"],
            "Haryana": ["Haryana", "HR"],
            "Odisha": ["Odisha", "Orissa", "OD"],
            "Kerala": ["Kerala", "KL"],
            "Jharkhand": ["Jharkhand", "JH"],
            "Assam": ["Assam", "AS"],
            "Chhattisgarh": ["Chhattisgarh", "CG", "C.G."],
            "Goa": ["Goa", "GA"]
        }
        
        self.major_cities = [
        "Mumbai", "Pune", "Delhi", "Bangalore", "Chennai", "Hyderabad",
        "Kolkata", "Ahmedabad", "Jaipur", "Lucknow", "Surat", "Bhopal",
        "Indore", "Nagpur", "Visakhapatnam", "Patna", "Chandigarh",
        "Coimbatore", "Thane", "Vadodara", "Ludhiana", "Agra", "Nashik"
    ]

        state_patterns = [self.nlp(text) 
                         for state_vars in self.states.values() 
                         for text in state_vars]
        self.phrase_matcher.add("STATE", state_patterns)
        
        city_patterns = [self.nlp(city) for city in self.major_cities]
        self.phrase_matcher.add("CITY", city_patterns)
    
    def _add_address_patterns(self):
        """Add enhanced patterns for Indian address components"""
        self.matcher.add("BUILDING", [
            [{"TEXT": {"REGEX": r"(?i)plot\s+(?:no\.?\s*)?[A-Za-z0-9\-]+"}}, {"OP": "?"}],
            [{"LOWER": {"IN": ["floor", "storey", "level"]}}, {"LIKE_NUM": True}],
            [{"TEXT": {"REGEX": r"(?i)\d+(?:st|nd|rd|th)\s+floor"}}],
            [{"TEXT": {"REGEX": r"(?i)(tower|block|wing)[s]?\s*[-]?\s*[A-Za-z0-9]+"}}]
        ])

        self.matcher.add("STREET", [
            [{"TEXT": {"REGEX": r"(?i)[A-Za-z\s\-]+(?:street|road|lane|avenue|boulevard|highway|marg|nagar)"}}, {"OP": "?"}],
            [{"TEXT": {"REGEX": r"(?i)[A-Za-z\s\-]+(?:complex|plaza|towers|society|colony|chowk)"}}, {"OP": "?"}],
            [{"LOWER": {"IN": ["block", "sector"]}}, {"TEXT": {"REGEX": r"[A-Za-z0-9\-]+"}}]
        ])

        self.matcher.add("LOCATION", [
            [{"ENT_TYPE": "GPE"}, {"OP": "?"}],
            [{"ENT_TYPE": "LOC"}, {"OP": "?"}],
            [{"TEXT": {"REGEX": r"(?i)(east|west|north|south|central)"}}, {"OP": "?"}]
        ])

        self.matcher.add("PINCODE", [
            [{"TEXT": {"REGEX": r"\b\d{6}\b"}}]  # Matches Indian PIN codes
        ])


    
    def _extract_components(self, doc: Doc) -> Dict[str, str]:
        def is_likely_valid_address(components):
            # More comprehensive validation
            min_required_components = ['city', 'street']
            
            # Ensure we have at least 2 key components
            if sum(1 for key in min_required_components if key in components) < 2:
                return False
            
            # Suspicious phrases to avoid
            suspicious_phrases = [
                'shall be final',
                'are involved',
                'difference is in',
                'dates fixed for',
                'hearing of a case',
                'where the main',
                'not be questioned'
            ]
            
            # Combine all component values
            full_text = ' '.join(components.values()).lower()
            
            # Check if any suspicious phrase is in the full text
            if any(phrase in full_text for phrase in suspicious_phrases):
                return False
            
            # Additional length checks
            if len(full_text) < 10 or len(full_text) > 300:
                return False
            
            # Expanded city validation
            valid_cities = set([
                'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 
                'kolkata', 'pune', 'ahmedabad', 'surat', 'jaipur',
                'bandra', 'u.s.a.', 'washington', 'new york', 
                'bandra-kurla', 'east', 'west'
            ])
            
            if 'city' in components:
                city = components['city'].lower()
                if city == 'india':
                    return False
                if city not in valid_cities and len(city) < 2:
                    return False
            
            return True

        # Initialize components
        components = defaultdict(str)
        
        # Normalize text
        text = ' '.join(doc.text.split())

        # Enhanced PIN code extraction
        postal_match = re.search(r'\b\d{3}\s*\d{3}\b', text)
        if postal_match:
            components['postal_code'] = postal_match.group(0).replace(" ", "")

        # Enhanced building/complex extraction
        building_patterns = [
            r'\b([A-Za-z0-9\s\.-]+(?:Tower|Chambers|Plaza|Bhavan|Centre|Complex|Towers|Society|Apartment|Edge|Building|House|Mall|Park|Villa|Heights|Exchange|Stock)s?)\b',
            r'\b(P\.?\s*J\.?\s*Towers)\b',
            r'\b([\w\s]+\s+Stock\s+Exchange)\b'
        ]
        
        for pattern in building_patterns:
            building_match = re.search(pattern, text, re.I)
            if building_match:
                components['building'] = building_match.group(1).strip()
                break

        # Enhanced street extraction
        street_patterns = [
            r'\b([\w\s\.-]+(?:Street|Road|Lane|Avenue|Boulevard|Highway|Marg|Path|Way|Expressway|Cross|Main|Circle|Block|Towers)s?)\b',
            r'\b(\d+\s*(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s*Street)\b',
            r'\b(Dalal\s+Street)\b',
            r'\b(Lyons\s+Range)\b'
        ]
        
        for pattern in street_patterns:
            street_match = re.search(pattern, text, re.I)
            if street_match:
                components['street'] = street_match.group(1).strip()
                break

        # Enhanced area/locality extraction
        area_patterns = [
            r'\b([A-Za-z\s()-]+(?:Area|Block|Sector|Phase|Colony|Nagar|Extension|Enclave|Complex|East|West|North|South|[EWNS])\b(?:\s*[\(\)][EWNS][)\)])?)',
            r'\b(Bandra-Kurla\s+Complex)\b',
            r'\b(Dept\.?\s*of\s*Corporate\s*Services)\b'
        ]
        
        for pattern in area_patterns:
            area_match = re.search(pattern, text, re.I)
            if area_match:
                area = area_match.group(1).strip()
                area = re.sub(r'\(\s*([EWNS])\s*\)', r' (\1)', area)
                components['area'] = area
                break

        # Enhanced city extraction
        city_patterns = [
            r'\b(Mumbai|Delhi|Bangalore|Hyderabad|Chennai|Kolkata|Pune|Ahmedabad|Surat|Jaipur|Bandra|Washington|New York)\b',
            r'\b(U\.?S\.?A\.?)\b',
            r'\b(Bandra-Kurla)\b'
        ]
        
        for pattern in city_patterns:
            city_match = re.search(pattern, text, re.I)
            if city_match:
                components['city'] = city_match.group(1).strip()
                break
        
        # Fallback to NER for city
        if not components.get('city'):
            for ent in doc.ents:
                if ent is not None and ent.label_ == 'GPE':
                    if not any(ent.text.lower() in v.lower() for v in components.values()):
                        components['city'] = ent.text
                        break

        # Clean components
        for key in list(components.keys()):
            value = components[key].strip()
            value = re.sub(r'\s+', ' ', value)
            value = re.sub(r',+$', '', value)  # Remove trailing commas
            if value:
                components[key] = value
            else:
                del components[key]

        # Final validation
        if is_likely_valid_address(components):
            return dict(components)
        
        return {}

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[,\t•⚫]+', ',', text)
        text = re.sub(r'\s*,\s*', ', ', text)
        return text.strip()

    def _extract_address_block(self, text: str) -> List[str]:
        """Extract address blocks using generic patterns and contextual clues"""
        blocks = []
        current_block = []
        
        # Split text into lines and clean each line
        lines = [line.strip() for line in text.split('\n')]
        
        # Generic patterns that typically indicate a new address
        address_indicators = [
            r'\b\d{6}\b',  # PIN code
            r'\b\d+[A-Za-z]?,\s*[A-Za-z\s]+',  # Street number followed by text
            r'\b[A-Za-z]+[\s-]+(?:Complex|Plaza|Towers|Building|Street|Road|Lane|Avenue)\b',  # Common address elements
            r'(?:^|\s)(?:Floor|Level|Block|Sector|Phase)\s+[A-Za-z0-9-]+\b'  # Common building/area elements
        ]
        
        for line in lines:
            if not line:
                if current_block:
                    blocks.append(' '.join(current_block))
                    current_block = []
                continue
            
            # Check if line likely starts a new address
            has_address_indicator = any(re.search(pattern, line, re.I) for pattern in address_indicators)
            
            # Start new block if current line has address indicators and previous block exists
            if has_address_indicator and current_block and not any(re.search(pattern, current_block[-1], re.I) for pattern in address_indicators):
                blocks.append(' '.join(current_block))
                current_block = []
            
            current_block.append(line)
        
        if current_block:
            blocks.append(' '.join(current_block))
        
        # Clean and normalize blocks
        cleaned_blocks = []
        for block in blocks:
            # Remove excessive whitespace and normalize separators
            cleaned = re.sub(r'\s+', ' ', block)
            cleaned = re.sub(r'[,\s]*,[,\s]*', ', ', cleaned)
            cleaned = cleaned.strip(' ,')
            if cleaned:
                cleaned_blocks.append(cleaned)
        
        return cleaned_blocks

    def _detect_region(self, text: str, components: Dict[str, str]) -> str:
        text_lower = text.lower()
        
        if 'state' in components:
            state = components['state']
            for region, info in self.regional_info.items():
                if any(s.lower() in state.lower() for s in info['states']):
                    return region
        
        if 'city' in components:
            city = components['city'].lower()
            for region, info in self.regional_info.items():
                if any(c.lower() in city for c in info['cities']):
                    return region
        
        for region, info in self.regional_info.items():
            if any(term in text_lower for term in info['terms']):
                return region
        
        return 'unknown'

    def extract_addresses(self, text: str, min_confidence: float = 0.3) -> List[AddressMatch]:
        try:
            addresses = []
            blocks = self._extract_address_block(text)
            
            for block in blocks:
                try:
                    doc = self.nlp(block)
                    components = self._extract_components(doc)
                    
                    confidence = self._calculate_confidence(components, block)
                    
                    if confidence >= min_confidence:
                        region = self._detect_region(block, components)
                        match = AddressMatch(
                            raw_text=block,
                            components=components,
                            confidence_score=confidence,
                            region=region
                        )
                        addresses.append(match)
                
                except Exception as e:
                    logger.warning(f"Error processing block: {block[:50]}... Error: {str(e)}")
                    continue
            
            return self._deduplicate_addresses(addresses)
            
        except Exception as e:
            logger.error(f"Error in address extraction: {str(e)}")
            return []

    def _calculate_confidence(self, components: Dict[str, str], text: str) -> float:
        """Calculate confidence score using generic criteria"""
        score = 0.0
        
        # Basic component presence scoring
        if components.get('postal_code'):
            score += 0.3
        if components.get('building') or components.get('street'):
            score += 0.3
        if components.get('city'):
            score += 0.2
        if components.get('area'):
            score += 0.1
        
        # Context-based scoring
        words = text.split()
        if len(words) >= 4:  # Minimum words for a likely address
            score += 0.1
        
        # Number of components
        component_count = sum(1 for v in components.values() if v)
        if component_count >= 3:
            score += 0.2
        
        # Check for numeric components (common in addresses)
        has_numbers = bool(re.search(r'\d', text))
        if has_numbers:
            score += 0.1
        
        return min(score, 1.0)

    def _deduplicate_addresses(self, addresses: List[AddressMatch]) -> List[AddressMatch]:
        unique_addresses = []
        seen_texts = set()
        
        for addr in addresses:
            normalized_text = re.sub(r'\s+', ' ', addr.raw_text.lower())
            if normalized_text not in seen_texts:
                seen_texts.add(normalized_text)
                unique_addresses.append(addr)
        
        return unique_addresses

    def format_address(self, address_match: AddressMatch) -> str:
        """Format address using a generic approach"""
        try:
            components = address_match.components
            parts = []
            
            # Add components in a logical order
            if 'building' in components:
                parts.append(components['building'])
            
            if 'street' in components:
                parts.append(components['street'])
            
            if 'area' in components:
                parts.append(components['area'])
            
            # Combine city and postal code
            location_part = []
            if 'city' in components:
                location_part.append(components['city'])
            if 'postal_code' in components:
                location_part.append(components['postal_code'])
            
            if location_part:
                parts.append(' - '.join(location_part))
            
            # Join all parts with commas
            formatted = ', '.join(filter(None, parts))
            formatted = re.sub(r'\s+', ' ', formatted)
            formatted = re.sub(r',\s*,', ',', formatted)
            
            return formatted.strip(' ,')
            
        except Exception as e:
            logger.error(f"Error formatting address: {str(e)}")
            return address_match.raw_text

def process_pdf_for_addresses(pdf_path: str) -> List[Dict]:
    """Process PDF file and extract addresses with improved accuracy"""
    try:
        with fitz.open(pdf_path) as pdf:
            pdf_text = ""
            for page in pdf:
                pdf_text += page.get_text() + "\n"

        extractor = IndianAddressExtractor()
        
        addresses = extractor.extract_addresses(pdf_text)

        formatted_addresses = []
        seen_addresses = set()
        
        for addr in addresses:
            formatted = extractor.format_address(addr)
            
            if len(addr.components) < 2:
                continue
                
            if formatted not in seen_addresses:
                seen_addresses.add(formatted)
                formatted_addresses.append({
                    'formatted': formatted,
                    'raw': addr.raw_text,
                    'confidence': addr.confidence_score,
                    'region': addr.region,
                    'components': addr.components
                })

        return formatted_addresses

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return []

def main():
    """Main function to process PDF and print addresses"""
    pdf_path = r"C:\Users\ACER\Downloads\Draft Agreement.pdf"
    
    if not Path(pdf_path).exists():
        print(f"File not found: {pdf_path}")
        return
    
    addresses = process_pdf_for_addresses(pdf_path)

    print("\nExtracted Addresses from PDF:")
    for addr in addresses:
        if addr['confidence'] > 0.7:  # Only print if confidence is greater than 0.7
            print("\n" + "=" * 50)
            print(f"Formatted: {addr['formatted']}")
            print(f"Confidence: {addr['confidence']:.2f}")
            print(f"Region: {addr['region']}")
            print("Components:", addr['components'])
            print("=" * 50)

if __name__ == "__main__":
    main()