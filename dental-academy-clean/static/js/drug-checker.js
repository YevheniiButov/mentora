// Функция для показа Drug Interaction Checker
function showDrugInteractionChecker(event) {
  if (event) {
    event.preventDefault();
  }
  
  let interactiesBlock = document.getElementById('interacties-checker-block');
  
  // Если блок не найден, создаем его
  if (!interactiesBlock) {

    // Создаем блок
    interactiesBlock = document.createElement('div');
    interactiesBlock.id = 'interacties-checker-block';
    interactiesBlock.style.margin = '2rem 0';
    
    // Получаем языковой префикс из URL
    const currentLang = window.location.pathname.split('/')[1] || 'nl';
    
    interactiesBlock.innerHTML = `
      <div class="card border-warning">
        <div class="card-header bg-warning text-dark">
          <h6 class="mb-0">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Live Drug Checker
          </h6>
        </div>
        <div class="card-body">
          <div class="drug-checker-widget">
            <div class="form-floating mb-2">
              <input type="text" class="form-control" placeholder="Medicijn 1..." id="drug1">
              <label for="drug1">Medicijn 1</label>
            </div>
            <div class="form-floating mb-3">
              <input type="text" class="form-control" placeholder="Medicijn 2..." id="drug2">
              <label for="drug2">Medicijn 2</label>
            </div>
            <button class="btn btn-warning w-100" onclick="quickInteractionCheck()">
              <i class="bi bi-search me-1"></i>
              Check Interactie
            </button>
            <div id="quickResult" class="mt-3"></div>
          </div>
          <hr>
          <a href="/${currentLang}/farmacie/advanced-drug-checker" class="btn btn-outline-warning w-100" id="advanced-checker-link">
            <i class="bi bi-gear me-1"></i>
            Geavanceerde Checker
          </a>
        </div>
      </div>
    `;
    
    // Добавляем блок в middle-column
    const middleColumn = document.querySelector('.middle-column');
    if (middleColumn) {
      middleColumn.appendChild(interactiesBlock);

    } else {
      console.error('❌ Не найден элемент .middle-column для добавления блока!');
      return;
    }
  }
  
  interactiesBlock.style.display = 'block';

  // Плавная прокрутка к блоку
  interactiesBlock.scrollIntoView({ 
    behavior: 'smooth', 
    block: 'start' 
  });
}

// Функция для быстрой проверки взаимодействий
function quickInteractionCheck() {
  const drug1 = document.getElementById('drug1').value.trim();
  const drug2 = document.getElementById('drug2').value.trim();
  const resultElement = document.getElementById('quickResult');
  
  if (!drug1 || !drug2) {
    resultElement.innerHTML = `
      <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        Vul beide medicijnen in om interacties te controleren
      </div>
    `;
    return;
  }
  
  // База данных взаимодействий (можно расширить)
  const knownInteractions = {
    'warfarine+ibuprofen': {
      severity: 'MAJOR', 
      warning: '⚠️ MAJOR: Verhoogd bloedingsrisico',
      description: 'Verhoogd risico op bloedingen door remming van bloedplaatjesaggregatie'
    },
    'digoxine+furosemide': {
      severity: 'MAJOR', 
      warning: '⚠️ MAJOR: Digitalis toxiciteit risico',
      description: 'Verhoogd risico op digitalis toxiciteit door hypokaliëmie'
    },
    'amiodarone+digoxine': {
      severity: 'MAJOR', 
      warning: '⚠️ MAJOR: Verhoogde digoxine concentratie',
      description: 'Verhoogde digoxine concentratie door remming van uitscheiding'
    },
    'simvastatine+amiodarone': {
      severity: 'MAJOR', 
      warning: '⚠️ MAJOR: Verhoogd risico op rhabdomyolyse',
      description: 'Verhoogd risico op spierschade door CYP3A4 remming'
    },
    'metoprolol+verapamil': {
      severity: 'MODERATE', 
      warning: '⚠️ MODERATE: Verhoogd risico op bradycardie',
      description: 'Additieve cardiodepressieve effecten'
    },
    'aspirine+clopidogrel': {
      severity: 'MAJOR', 
      warning: '⚠️ MAJOR: Verhoogd bloedingsrisico',
      description: 'Dubbele antiplaatjeswerking verhoogt bloedingsrisico'
    },
    'paracetamol+ibuprofen': {
      severity: 'MINOR', 
      warning: 'ℹ️ MINOR: Geen klinisch relevante interactie',
      description: 'Combinatie wordt vaak gebruikt voor pijnbestrijding'
    },
    'omeprazol+clopidogrel': {
      severity: 'MODERATE', 
      warning: '⚠️ MODERATE: Verminderde effectiviteit clopidogrel',
      description: 'CYP2C19 remming vermindert activatie van clopidogrel'
    }
  };
  
  // Проверяем взаимодействие
  const key1 = `${drug1.toLowerCase()}+${drug2.toLowerCase()}`;
  const key2 = `${drug2.toLowerCase()}+${drug1.toLowerCase()}`;
  const interaction = knownInteractions[key1] || knownInteractions[key2];
  
  if (interaction) {
    // Определяем класс для уровня опасности
    let alertClass = 'alert-info';
    let icon = 'bi-info-circle';
    
    if (interaction.severity === 'MAJOR') {
      alertClass = 'alert-danger';
      icon = 'bi-exclamation-triangle-fill';
    } else if (interaction.severity === 'MODERATE') {
      alertClass = 'alert-warning';
      icon = 'bi-exclamation-triangle';
    } else if (interaction.severity === 'MINOR') {
      alertClass = 'alert-success';
      icon = 'bi-check-circle';
    }
    
    resultElement.innerHTML = `
      <div class="alert ${alertClass}">
        <div class="d-flex align-items-center">
          <i class="${icon} me-2" style="font-size: 1.5rem;"></i>
          <div>
            <h6 class="mb-1">${interaction.warning}</h6>
            <p class="mb-0">${interaction.description}</p>
          </div>
        </div>
      </div>
    `;
  } else {
    resultElement.innerHTML = `
      <div class="alert alert-success">
        <div class="d-flex align-items-center">
          <i class="bi bi-check-circle me-2" style="font-size: 1.5rem;"></i>
          <div>
            <h6 class="mb-1">Geen bekende interactie gevonden</h6>
            <p class="mb-0">Er is geen significante interactie bekend tussen deze medicijnen.</p>
          </div>
        </div>
      </div>
    `;
  }
  
  // Показываем результат с анимацией
  resultElement.style.opacity = '0';
  resultElement.style.display = 'block';
  setTimeout(() => {
    resultElement.style.transition = 'opacity 0.3s ease';
    resultElement.style.opacity = '1';
  }, 10);
}

// Автоматически инициализируем функцию, если в URL есть "interacties"
document.addEventListener('DOMContentLoaded', function() {
  if (window.location.href.toLowerCase().includes('interacties') || 
      window.location.href.toLowerCase().includes('contraindicaties')) {
    showDrugInteractionChecker();
  }
}); 