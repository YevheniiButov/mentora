# scripts/setup_virtual_patient.py

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, VirtualPatientScenario
from flask import g

def setup_virtual_patient():
    """Run all steps to set up the virtual patient module"""
    print("🔧 Setting up virtual patient module...")
    
    # Step 1: Create database tables
    print("\n📊 Step 1: Creating database tables...")
    try:
        with app.app_context():
            # Set up a fake request context for g.lang
            g.lang = 'en'
            
            # Create all tables
            db.create_all()
            print("✅ Virtual patient tables have been created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    
    # Step 2: Create demo scenario
    print("\n📚 Step 2: Creating demo scenario...")
    try:
        with app.app_context():
            # Set up a fake request context for g.lang
            g.lang = 'en'
            
            # Check if demo scenario already exists
            existing = VirtualPatientScenario.query.filter_by(
                title="Болезненная пломба"
            ).first()
            
            if existing:
                print("Demo scenario already exists, skipping creation.")
            else:
                # Create the demo scenario (simplified code here)
                create_demo_scenario()
    except Exception as e:
        print(f"❌ Error creating demo scenario: {e}")
        print("Continuing with setup anyway...")
    
    # Step 3: Set up images directory
    print("\n🖼️ Step 3: Setting up virtual patient images...")
    try:
        # Get the static folder path
        static_folder = app.static_folder if hasattr(app, 'static_folder') else 'static'
        
        # Create the virtual_patients directory in the static/images folder
        vp_dir = os.path.join(static_folder, 'images', 'virtual_patients')
        os.makedirs(vp_dir, exist_ok=True)
        
        # Check if we already have the patient image
        patient_image_path = os.path.join(vp_dir, 'patient_maria.jpg')
        
        if os.path.exists(patient_image_path):
            print(f"Image already exists at {patient_image_path}")
        else:
            print(f"Please manually add a patient image at: {patient_image_path}")
    except Exception as e:
        print(f"❌ Error setting up virtual patient images: {e}")
        print("Please manually create the directory 'static/images/virtual_patients/'")
        print("and add an image named 'patient_maria.jpg' in that directory.")
    
    print("\n✅ Virtual patient module setup complete!")
    print("\nYou can now access the virtual patient module at:")
    print("  - http://localhost:5000/en/virtual-patient/ (English)")
    print("  - http://localhost:5000/ru/virtual-patient/ (Russian)")
    
    return True

def create_demo_scenario():
    """Create a demo scenario for the virtual patient module"""
    scenario = VirtualPatientScenario(
        title="Болезненная пломба",
        description="Пациент жалуется на боль при жевании после установки пломбы на нижний моляр.",
        difficulty="easy",
        category="restorative",
        is_premium=False,
        is_published=True,
        max_score=100,
        scenario_data='{"default":{"patient_info":{"name":"Maria van der Berg","age":45,"gender":"female","image":"patient_maria.jpg","medical_history":"Diabetes type 2, hypertension"},"initial_state":{"node_id":"start","patient_statement":"Hello doctor, I have pain in my back teeth after the filling you did last week. It hurts when I drink cold water.","patient_emotion":"concerned","notes":"Patient had a deep caries on tooth 36, filled with composite last week. Pulp was not exposed during treatment."},"dialogue_nodes":[{"id":"start","options":[{"text":"I\'m sorry to hear that. Can you point exactly where the pain is located?","next_node":"location","score":10},{"text":"It\'s normal to have sensitivity after a filling. It will go away.","next_node":"dismissal","score":-5},{"text":"Let me take a look at your tooth.","next_node":"examination","score":5}]},{"id":"location","patient_statement":"It\'s this one, the lower left molar. The pain shoots up when I drink something cold and it lasts for about 10 seconds.","patient_emotion":"pointing","options":[{"text":"Does it hurt when you bite or chew?","next_node":"bite_pain","score":10},{"text":"Let me check your bite with articulating paper.","next_node":"examination","score":8},{"text":"I\'ll take an X-ray to check the filling.","next_node":"xray","score":5}]},{"id":"examination","patient_statement":"It feels most painful when I bite here.","patient_emotion":"pointing","options":[{"text":"I see the problem. The filling is too high and needs adjustment.","next_node":"treatment","score":20},{"text":"Let\'s take an X-ray to check for hidden problems.","next_node":"xray","score":-5},{"text":"The nerve might be irritated. We should consider root canal treatment.","next_node":"wrong_treatment","score":-15}]},{"id":"treatment","patient_statement":"So you can fix it today?","patient_emotion":"happy","options":[{"text":"Yes, I\'ll adjust the filling now. It\'s a simple procedure.","next_node":"success","score":10},{"text":"Let me reduce the high spots on your filling. Bite down on this paper.","next_node":"success","score":15},{"text":"I\'ll fix it, but you might need to come back if it still hurts.","next_node":"partial_success","score":5}]},{"id":"success","patient_statement":"That feels so much better! Now my teeth come together naturally. Thank you!","patient_emotion":"happy","options":[]}],"outcomes":{"correct_diagnosis":{"text":"Excellent diagnosis! You correctly identified the high filling causing pain on occlusion and adjusted it appropriately.","min_score":70,"badge":"clinical_reasoning_1"},"partial_diagnosis":{"text":"You identified the issue, but your communication with the patient could have been more effective.","min_score":40,"badge":null},"incorrect_diagnosis":{"text":"You missed key diagnostic steps and did not address the patient\'s concerns effectively.","min_score":0,"badge":null}}},"translations":{"ru":{"patient_info":{"name":"Мария ван дер Берг","age":45,"gender":"female","image":"patient_maria.jpg","medical_history":"Диабет 2 типа, гипертония"},"initial_state":{"node_id":"start","patient_statement":"Здравствуйте, доктор. У меня болит задний зуб после установки пломбы на прошлой неделе. Особенно больно, когда я пью холодную воду.","patient_emotion":"concerned","notes":"Пациентке была установлена пломба на глубокую кариозную полость в зубе 36 неделю назад. Пульпа не была обнажена во время лечения."},"dialogue_nodes":[{"id":"start","options":[{"text":"Мне жаль это слышать. Можете указать точно, где локализуется боль?","next_node":"location","score":10},{"text":"Повышенная чувствительность после пломбирования — это нормально. Она пройдет.","next_node":"dismissal","score":-5},{"text":"Давайте я осмотрю ваш зуб.","next_node":"examination","score":5}]},{"id":"location","patient_statement":"Вот этот, нижний левый моляр. Боль простреливает, когда я пью что-то холодное, и длится около 10 секунд.","patient_emotion":"pointing","options":[{"text":"Болит ли при накусывании или жевании?","next_node":"bite_pain","score":10},{"text":"Давайте проверим ваш прикус с помощью артикуляционной бумаги.","next_node":"examination","score":8},{"text":"Сделаем рентгеновский снимок, чтобы проверить пломбу.","next_node":"xray","score":5}]},{"id":"examination","patient_statement":"Больнее всего, когда я кусаю вот здесь.","patient_emotion":"pointing","options":[{"text":"Я вижу проблему. Пломба слишком высокая и требует коррекции.","next_node":"treatment","score":20},{"text":"Давайте сделаем рентген, чтобы проверить скрытые проблемы.","next_node":"xray","score":-5},{"text":"Возможно, нерв раздражен. Нам стоит рассмотреть лечение корневых каналов.","next_node":"wrong_treatment","score":-15}]},{"id":"treatment","patient_statement":"Так вы можете исправить это сегодня?","patient_emotion":"happy","options":[{"text":"Да, я скорректирую пломбу прямо сейчас. Это простая процедура.","next_node":"success","score":10},{"text":"Я уменьшу высокие участки на вашей пломбе. Прикусите эту бумагу.","next_node":"success","score":15},{"text":"Я исправлю это, но возможно придется прийти снова, если боль сохранится.","next_node":"partial_success","score":5}]},{"id":"success","patient_statement":"Так намного лучше! Теперь зубы смыкаются естественно. Спасибо!","patient_emotion":"happy","options":[]}],"outcomes":{"correct_diagnosis":{"text":"Отличный диагноз! Вы правильно определили, что высокая пломба вызывает боль при окклюзии, и соответствующим образом скорректировали её.","min_score":70,"badge":"clinical_reasoning_1"},"partial_diagnosis":{"text":"Вы определили проблему, но ваше общение с пациентом могло бы быть более эффективным.","min_score":40,"badge":null},"incorrect_diagnosis":{"text":"Вы упустили ключевые диагностические шаги и неэффективно отреагировали на жалобы пациента.","min_score":0,"badge":null}}}}}}'
    )
    
    db.session.add(scenario)
    db.session.commit()
    
    print("✅ Demo scenario created successfully!")
    return True

if __name__ == "__main__":
    setup_virtual_patient()