import re

def extract_address(text):
    # Improved regex pattern for more comprehensive address extraction
    address_pattern = r"(\d{1,5}[\w\s.,/-]+(?:Building|Street|Room|Annexe|Head\sOffice|Municipal\sHead\sOffice|Marg|India|Phase|\w+)[\w\s.,/-]*\d{6}|\d{3,4}\s(?:Mumbai|India|[A-Za-z\s]+))"
    
    # Search for the address in the text using the regex pattern
    address_match = re.findall(address_pattern, text)
    
    if address_match:
        # Extract and return the first address match
        return address_match[0]
    else:
        return "No address found"

# Example usage
text = """
    A G R E E M E N T
 This Agreement is made and entered into at Mumbai, and effective on this
 __________ day of____________ of Two Thousand Eighteen.
 BETWEEN
 The Municipal Corporation of Greater Mumbai a body corporate having
 perpetual succession and a common seal constituted by the Mumbai Municipal
 Corporation Act 1888, hereinafter referred to “MCGM” 
REPRESENTED BY 
Smt. Nidhi Choudhari, Deputy Municipal Commissioner (Special), having
 office at 3rd Floor, Annexe Building, Municipal Head Office, Mahapalika Marg,
 Mumbai- 400001, hereinafter referred to as “DMC(Special)” (which expression shall
 unless repugnant to the context or meaning thereof be deemed to mean and include
 the successor or successors for the time being holding the office of the Deputy
 Municipal Commissioner (Special)) of the First Part;
 AND
 Shri/ Smt. ________________________________, an Indian Inhabitant of
 Mumbai, residing at ___________________________________________________,
 having Sanad Registration No. ________________________ of ___________  and
 being the Member of _______________ Bar Association of the ____________ Court;
 hereinafter referred to as “Sr. Panel Advocate”  (which expression shall unless
 repugnant to the context or meaning thereof be deemed to mean and include 
                             A G R E E M E N T
 
Mr. J. J. Xavier
 Advocate & Law Officer 
Legal Department, MCGM
 Room No. 311, 3rd Floor, 
Annexe Building, Municipal 
Head Office, Mahapalika Marg, 
Mumbai:- 400 001
 13

"""

addresses = extract_address(text)
print(f"Extracted Address: {addresses}")