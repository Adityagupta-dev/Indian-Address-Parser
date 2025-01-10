import spacy
from spacy.training.example import Example
from spacy.tokens import DocBin
from spacy.util import minibatch
import random
import os

class AddressNERTrainer:
    def __init__(self):
        self.labels = ["ROOM_NO", "BUILDING_NAME", "LANDMARK", "STREET", "AREA", "STATE", "CITY", "PINCODE"]
        
    def create_model(self):
        """Create a new blank model with NER pipeline"""
        nlp = spacy.blank("en")
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner")
            
            # Add labels
            for label in self.labels:
                ner.add_label(label)
        
        return nlp
    
    def train_model(self, train_path, output_dir, n_iter=30):
        """Train the NER model"""
        try:
            # Check if training data exists
            if not os.path.exists(train_path):
                raise FileNotFoundError(f"Training data not found at {train_path}")

            print("Creating new model...")
            nlp = self.create_model()
            
            # Load training data
            print("Loading training data...")
            train_examples = []
            doc_bin = DocBin().from_disk(train_path)
            docs = list(doc_bin.get_docs(nlp.vocab))
            
            print(f"Converting {len(docs)} documents to training examples...")
            for doc in docs:
                train_examples.append(
                    Example.from_dict(
                        nlp.make_doc(doc.text), 
                        {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}
                    )
                )
            
            # Configure training
            print("Starting training...")
            optimizer = nlp.begin_training()
            batch_size = 4
            
            # Start training
            for iteration in range(n_iter):
                random.shuffle(train_examples)
                losses = {}
                
                batches = list(minibatch(train_examples, size=batch_size))
                total_batches = len(batches)
                
                for batch_index, batch in enumerate(batches):
                    nlp.update(batch, drop=0.5, losses=losses)
                    
                    # Print progress
                    if (batch_index + 1) % 10 == 0:
                        print(f"Iteration {iteration + 1}/{n_iter}, Batch {batch_index + 1}/{total_batches}")
                
                print(f"Iteration {iteration + 1}/{n_iter} completed. Losses: {losses}")
            
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save the model
            print(f"Saving model to {output_dir}...")
            nlp.to_disk(output_dir)
            print("Model training completed successfully!")
            
            return nlp
            
        except Exception as e:
            print(f"Error during training: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        trainer = AddressNERTrainer()
        trainer.train_model("train.spacy", "address_ner_model")
    except Exception as e:
        print(f"Training failed: {str(e)}")
