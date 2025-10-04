import json
import os

def validate_json_files():
    """Validate the generated JSON files"""
    
    print("=" * 60)
    print("JSON File Validation")
    print("=" * 60)
    
    # Check connect.json
    connect_path = "connect.json"
    if os.path.exists(connect_path):
        print(f"\n✓ {connect_path} exists")
        with open(connect_path, 'r', encoding='utf-8') as f:
            connect_data = json.load(f)
        
        print(f"  Metadata keys: {list(connect_data['metadata'].keys())}")
        print(f"  Total sections: {len(connect_data['sections'])}")
        print(f"  Metadata values:")
        for key, value in connect_data['metadata'].items():
            print(f"    - {key}: {value}")
        
        if connect_data['sections']:
            print(f"  Sample section keys: {list(connect_data['sections'][0].keys())}")
            sample = connect_data['sections'][0]
            print(f"  Sample section: {sample['courseCode']} - Section {sample.get('sectionName', 'N/A')}")
        
        file_size = os.path.getsize(connect_path)
        print(f"  File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    else:
        print(f"\n✗ {connect_path} not found!")
    
    # Check exams.json
    exams_path = "exams.json"
    if os.path.exists(exams_path):
        print(f"\n✓ {exams_path} exists")
        with open(exams_path, 'r', encoding='utf-8') as f:
            exams_data = json.load(f)
        
        print(f"  Metadata keys: {list(exams_data['metadata'].keys())}")
        print(f"  Total exams: {len(exams_data['exams'])}")
        print(f"  Metadata values:")
        for key, value in exams_data['metadata'].items():
            print(f"    - {key}: {value}")
        
        if exams_data['exams']:
            print(f"  Sample exam keys: {list(exams_data['exams'][0].keys())}")
            sample = exams_data['exams'][0]
            print(f"  Sample exam: {sample['courseCode']} - Section {sample.get('sectionName', 'N/A')}")
            
            # Check for null exam dates (lab sections)
            null_count = sum(1 for exam in exams_data['exams'] 
                           if exam['midExamDate'] is None and exam['finalExamDate'] is None)
            print(f"  Sections with no exams (labs): {null_count}")
        
        file_size = os.path.getsize(exams_path)
        print(f"  File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    else:
        print(f"\n✗ {exams_path} not found!")
    
    # Check index.html
    index_path = "index.html"
    if os.path.exists(index_path):
        print(f"\n✓ {index_path} exists")
        file_size = os.path.getsize(index_path)
        print(f"  File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    else:
        print(f"\n✗ {index_path} not found!")
    
    print("\n" + "=" * 60)
    print("✓ Validation Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open index.html in a browser to test the UI")
    print("2. Initialize Git repository: git init")
    print("3. Add files: git add .")
    print("4. Commit: git commit -m 'Initial commit'")
    print("5. Push to GitHub and enable GitHub Pages")

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    validate_json_files()
