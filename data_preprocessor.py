import spacy
from spacy.tokens import DocBin
import json

class AddressDataPreprocessor:
    def load_data(self, input_file):
        """Load data from a JSON file"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def convert_to_spacy_format(self, data, output_file):
        """Convert data to spaCy format and save to disk"""
        nlp = spacy.blank("en")
        db = DocBin()
        
        for item in data:
            doc = nlp.make_doc(item["text"])
            ents = []
            for label, text in item["annotations"].items():
                start = item["text"].find(text)
                end = start + len(text)
                span = doc.char_span(start, end, label=label.upper())
                if span is not None:
                    ents.append(span)
            
            # Ensure no overlapping entities
            ents = spacy.util.filter_spans(ents)
            doc.ents = ents
            db.add(doc)
        
        db.to_disk(output_file)
        return output_file

    def split_data(self, data, train_ratio=0.8):
        """Split data into training and testing sets"""
        split_idx = int(len(data) * train_ratio)
        train_data = data[:split_idx]
        test_data = data[split_idx:]
        
        self.convert_to_spacy_format(train_data, "train.spacy")
        self.convert_to_spacy_format(test_data, "test.spacy")
        
        return train_data, test_data

if __name__ == "__main__":
    preprocessor = AddressDataPreprocessor()
    data = preprocessor.load_data("address_dataset.json")
    train_data, test_data = preprocessor.split_data(data)