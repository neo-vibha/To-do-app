"""
AI Todo App - Intelligent Multilingual Task Management
Created according to PRD specifications with hybrid translation system
"""

import streamlit as st
import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Integration (uncomment when using real API)
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.warning("OpenAI library not installed. Using mock translations.")

class Priority(Enum):
    LOW = "🟢 Low"
    MEDIUM = "🟡 Medium" 
    HIGH = "🔴 High"

class Status(Enum):
    TODO = "📝 Todo"
    IN_PROGRESS = "⏳ In Progress"
    COMPLETED = "✅ Completed"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    tags: List[str] = None
    translations: Dict[str, Dict[str, str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.translations is None:
            self.translations = {}

class AITodoApp:
    def __init__(self):
        """Initialize the AI Todo App"""
        self.init_session_state()
        self.setup_predefined_translations()
        self.setup_openai_client()
        
    def init_session_state(self):
        """Initialize Streamlit session state"""
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []
        if 'selected_language' not in st.session_state:
            st.session_state.selected_language = 'English'
        if 'translation_cache' not in st.session_state:
            st.session_state.translation_cache = {}
        if 'api_usage_count' not in st.session_state:
            st.session_state.api_usage_count = 0
            
    def setup_predefined_translations(self):
        """Setup predefined translation dictionary for 5 languages"""
        self.predefined_translations = {
            # UI Elements
            'ui': {
                'English': {
                    'app_title': 'AI Todo App',
                    'app_subtitle': 'Intelligent Multilingual Task Management',
                    'add_task': 'Add New Task',
                    'task_title': 'Task Title',
                    'task_description': 'Task Description', 
                    'priority': 'Priority',
                    'status': 'Status',
                    'tags': 'Tags (comma-separated)',
                    'create_task': 'Create Task',
                    'update_task': 'Update Task',
                    'delete_task': 'Delete Task',
                    'translate': 'Translate',
                    'language': 'Language',
                    'filter_by_status': 'Filter by Status',
                    'filter_by_priority': 'Filter by Priority',
                    'search_tasks': 'Search Tasks',
                    'no_tasks_found': 'No tasks found. Create your first task!',
                    'translation_cached': 'Translation cached',
                    'translation_from_gpt': 'Translated with AI',
                    'translation_from_dict': 'Quick translation',
                    'api_error': 'Translation service unavailable',
                    'all': 'All'
                },
                'Spanish': {
                    'app_title': 'App de Tareas IA',
                    'app_subtitle': 'Gestión Inteligente de Tareas Multiidioma',
                    'add_task': 'Agregar Nueva Tarea',
                    'task_title': 'Título de la Tarea',
                    'task_description': 'Descripción de la Tarea',
                    'priority': 'Prioridad',
                    'status': 'Estado',
                    'tags': 'Etiquetas (separadas por comas)',
                    'create_task': 'Crear Tarea',
                    'update_task': 'Actualizar Tarea',
                    'delete_task': 'Eliminar Tarea',
                    'translate': 'Traducir',
                    'language': 'Idioma',
                    'filter_by_status': 'Filtrar por Estado',
                    'filter_by_priority': 'Filtrar por Prioridad',
                    'search_tasks': 'Buscar Tareas',
                    'no_tasks_found': '¡No se encontraron tareas. Crea tu primera tarea!',
                    'translation_cached': 'Traducción almacenada',
                    'translation_from_gpt': 'Traducido con IA',
                    'translation_from_dict': 'Traducción rápida',
                    'api_error': 'Servicio de traducción no disponible',
                    'all': 'Todos'
                },
                'French': {
                    'app_title': 'App Todo IA',
                    'app_subtitle': 'Gestion Intelligente de Tâches Multilingue',
                    'add_task': 'Ajouter Nouvelle Tâche',
                    'task_title': 'Titre de la Tâche',
                    'task_description': 'Description de la Tâche',
                    'priority': 'Priorité',
                    'status': 'Statut',
                    'tags': 'Étiquettes (séparées par virgules)',
                    'create_task': 'Créer Tâche',
                    'update_task': 'Mettre à Jour Tâche',
                    'delete_task': 'Supprimer Tâche',
                    'translate': 'Traduire',
                    'language': 'Langue',
                    'filter_by_status': 'Filtrer par Statut',
                    'filter_by_priority': 'Filtrer par Priorité',
                    'search_tasks': 'Rechercher Tâches',
                    'no_tasks_found': 'Aucune tâche trouvée. Créez votre première tâche!',
                    'translation_cached': 'Traduction mise en cache',
                    'translation_from_gpt': 'Traduit avec IA',
                    'translation_from_dict': 'Traduction rapide',
                    'api_error': 'Service de traduction indisponible',
                    'all': 'Tous'
                },
                'German': {
                    'app_title': 'KI Todo App',
                    'app_subtitle': 'Intelligente Mehrsprachige Aufgabenverwaltung',
                    'add_task': 'Neue Aufgabe Hinzufügen',
                    'task_title': 'Aufgabentitel',
                    'task_description': 'Aufgabenbeschreibung',
                    'priority': 'Priorität',
                    'status': 'Status',
                    'tags': 'Tags (durch Kommas getrennt)',
                    'create_task': 'Aufgabe Erstellen',
                    'update_task': 'Aufgabe Aktualisieren',
                    'delete_task': 'Aufgabe Löschen',
                    'translate': 'Übersetzen',
                    'language': 'Sprache',
                    'filter_by_status': 'Nach Status Filtern',
                    'filter_by_priority': 'Nach Priorität Filtern',
                    'search_tasks': 'Aufgaben Suchen',
                    'no_tasks_found': 'Keine Aufgaben gefunden. Erstellen Sie Ihre erste Aufgabe!',
                    'translation_cached': 'Übersetzung zwischengespeichert',
                    'translation_from_gpt': 'Mit KI übersetzt',
                    'translation_from_dict': 'Schnellübersetzung',
                    'api_error': 'Übersetzungsdienst nicht verfügbar',
                    'all': 'Alle'
                },
                'Italian': {
                    'app_title': 'App Todo IA',
                    'app_subtitle': 'Gestione Intelligente Attività Multilingue',
                    'add_task': 'Aggiungi Nuova Attività',
                    'task_title': 'Titolo Attività',
                    'task_description': 'Descrizione Attività',
                    'priority': 'Priorità',
                    'status': 'Stato',
                    'tags': 'Tag (separati da virgole)',
                    'create_task': 'Crea Attività',
                    'update_task': 'Aggiorna Attività',
                    'delete_task': 'Elimina Attività',
                    'translate': 'Traduci',
                    'language': 'Lingua',
                    'filter_by_status': 'Filtra per Stato',
                    'filter_by_priority': 'Filtra per Priorità',
                    'search_tasks': 'Cerca Attività',
                    'no_tasks_found': 'Nessuna attività trovata. Crea la tua prima attività!',
                    'translation_cached': 'Traduzione memorizzata',
                    'translation_from_gpt': 'Tradotto con IA',
                    'translation_from_dict': 'Traduzione veloce',
                    'api_error': 'Servizio di traduzione non disponibile',
                    'all': 'Tutti'
                },
                'Hindi': {
                    'app_title': 'एआई टूडू ऐप',
                    'app_subtitle': 'बुद्धिमान बहुभाषी कार्य प्रबंधन',
                    'add_task': 'नया कार्य जोड़ें',
                    'task_title': 'कार्य शीर्षक',
                    'task_description': 'कार्य विवरण',
                    'priority': 'प्राथमिकता',
                    'status': 'स्थिति',
                    'tags': 'टैग (कॉमा से अलग करें)',
                    'create_task': 'कार्य बनाएं',
                    'update_task': 'कार्य अपडेट करें',
                    'delete_task': 'कार्य हटाएं',
                    'translate': 'अनुवाद करें',
                    'language': 'भाषा',
                    'filter_by_status': 'स्थिति के अनुसार फ़िल्टर करें',
                    'filter_by_priority': 'प्राथमिकता के अनुसार फ़िल्टर करें',
                    'search_tasks': 'कार्य खोजें',
                    'no_tasks_found': 'कोई कार्य नहीं मिला। अपना पहला कार्य बनाएं!',
                    'translation_cached': 'अनुवाद संग्रहीत',
                    'translation_from_gpt': 'एआई से अनुवादित',
                    'translation_from_dict': 'त्वरित अनुवाद',
                    'api_error': 'अनुवाद सेवा उपलब्ध नहीं',
                    'all': 'सभी'
                }
            },
            # Common task phrases
            'tasks': {
                'English': {
                    'buy_groceries': 'Buy groceries',
                    'call_doctor': 'Call doctor',
                    'finish_project': 'Finish project',
                    'pay_bills': 'Pay bills',
                    'clean_house': 'Clean house',
                    'exercise': 'Exercise',
                    'study': 'Study',
                    'meeting': 'Meeting',
                    'deadline': 'Deadline',
                    'urgent': 'Urgent',
                    'important': 'Important',
                    'work': 'Work',
                    'personal': 'Personal',
                    'health': 'Health',
                    'finance': 'Finance',
                    'shopping': 'Shopping',
                    'appointment': 'Appointment'
                },
                'Spanish': {
                    'buy_groceries': 'Comprar comestibles',
                    'call_doctor': 'Llamar al doctor',
                    'finish_project': 'Terminar proyecto',
                    'pay_bills': 'Pagar facturas',
                    'clean_house': 'Limpiar casa',
                    'exercise': 'Hacer ejercicio',
                    'study': 'Estudiar',
                    'meeting': 'Reunión',
                    'deadline': 'Fecha límite',
                    'urgent': 'Urgente',
                    'important': 'Importante',
                    'work': 'Trabajo',
                    'personal': 'Personal',
                    'health': 'Salud',
                    'finance': 'Finanzas',
                    'shopping': 'Compras',
                    'appointment': 'Cita'
                },
                'French': {
                    'buy_groceries': 'Acheter des courses',
                    'call_doctor': 'Appeler le docteur',
                    'finish_project': 'Terminer le projet',
                    'pay_bills': 'Payer les factures',
                    'clean_house': 'Nettoyer la maison',
                    'exercise': 'Faire de l\'exercice',
                    'study': 'Étudier',
                    'meeting': 'Réunion',
                    'deadline': 'Date limite',
                    'urgent': 'Urgent',
                    'important': 'Important',
                    'work': 'Travail',
                    'personal': 'Personnel',
                    'health': 'Santé',
                    'finance': 'Finance',
                    'shopping': 'Achats',
                    'appointment': 'Rendez-vous'
                },
                'German': {
                    'buy_groceries': 'Lebensmittel kaufen',
                    'call_doctor': 'Arzt anrufen',
                    'finish_project': 'Projekt beenden',
                    'pay_bills': 'Rechnungen bezahlen',
                    'clean_house': 'Haus putzen',
                    'exercise': 'Sport treiben',
                    'study': 'Lernen',
                    'meeting': 'Besprechung',
                    'deadline': 'Frist',
                    'urgent': 'Dringend',
                    'important': 'Wichtig',
                    'work': 'Arbeit',
                    'personal': 'Persönlich',
                    'health': 'Gesundheit',
                    'finance': 'Finanzen',
                    'shopping': 'Einkaufen',
                    'appointment': 'Termin'
                },
                'Italian': {
                    'buy_groceries': 'Comprare generi alimentari',
                    'call_doctor': 'Chiamare il dottore',
                    'finish_project': 'Finire il progetto',
                    'pay_bills': 'Pagare le bollette',
                    'clean_house': 'Pulire casa',
                    'exercise': 'Fare esercizio',
                    'study': 'Studiare',
                    'meeting': 'Riunione',
                    'deadline': 'Scadenza',
                    'urgent': 'Urgente',
                    'important': 'Importante',
                    'work': 'Lavoro',
                    'personal': 'Personale',
                    'health': 'Salute',
                    'finance': 'Finanza',
                    'shopping': 'Shopping',
                    'appointment': 'Appuntamento'
                },
                'Hindi': {
                    'buy_groceries': 'किराना खरीदना',
                    'call_doctor': 'डॉक्टर को कॉल करना',
                    'finish_project': 'प्रोजेक्ट पूरा करना',
                    'pay_bills': 'बिल भुगतान',
                    'clean_house': 'घर साफ करना',
                    'exercise': 'व्यायाम',
                    'study': 'अध्ययन',
                    'meeting': 'बैठक',
                    'deadline': 'समय सीमा',
                    'urgent': 'तत्काल',
                    'important': 'महत्वपूर्ण',
                    'work': 'काम',
                    'personal': 'व्यक्तिगत',
                    'health': 'स्वास्थ्य',
                    'finance': 'वित्त',
                    'shopping': 'खरीदारी',
                    'appointment': 'अपॉइंटमेंट'
                }
            }
        }
        
        self.supported_languages = ['English', 'Spanish', 'French', 'German', 'Italian', 'Hindi']
        
    def setup_openai_client(self):
        """Initialize OpenAI client"""
        self.openai_client = None
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not OPENAI_AVAILABLE:
            return
            
        if api_key and api_key.startswith('sk-'):
            try:
                self.openai_client = OpenAI(api_key=api_key)
                # Test the connection with a minimal call
                try:
                    self.openai_client.models.list()
                except Exception as test_error:
                    st.warning(f"⚠️ OpenAI API test failed: {str(test_error)}")
                    self.openai_client = None
            except Exception as e:
                st.error(f"OpenAI client initialization failed: {str(e)}")
                self.openai_client = None
        elif not api_key:
            # Only show this message once per session
            if 'api_key_warning_shown' not in st.session_state:
                st.info("💡 Add OPENAI_API_KEY to environment variables for AI translations.")
                st.session_state.api_key_warning_shown = True
    
    def get_ui_text(self, key: str, language: str = None) -> str:
        """Get UI text in specified language"""
        if language is None:
            language = st.session_state.selected_language
        return self.predefined_translations['ui'].get(language, {}).get(key, key)
    
    def translate_text_with_dictionary(self, text: str, target_language: str) -> Optional[str]:
        """First attempt: Check predefined dictionary"""
        # Normalize text for lookup
        normalized_text = text.lower().strip().replace(' ', '_').replace('.', '').replace(',', '').replace('!', '').replace('?', '')
        
        # Check UI translations
        ui_translation = self.predefined_translations['ui'].get(target_language, {}).get(normalized_text)
        if ui_translation:
            return ui_translation
            
        # Check task translations
        task_translation = self.predefined_translations['tasks'].get(target_language, {}).get(normalized_text)
        if task_translation:
            return task_translation
            
        # Check for partial matches in common words
        for key, value in self.predefined_translations['tasks'].get(target_language, {}).items():
            if normalized_text in key or key in normalized_text:
                return value
                
        return None
    
    def translate_text_with_gpt(self, text: str, target_language: str) -> str:
        """Second attempt: Use GPT-4 for translation"""
        if not self.openai_client:
            return f"[Mock AI Translation to {target_language}] {text}"
        
        try:
            # Handle translation to English specifically
            if target_language == 'English':
                system_prompt = "You are a professional translator. Translate the given text to English. Return only the English translation, no additional text or explanations."
            else:
                system_prompt = f"You are a professional translator. Translate the given text to {target_language}. Return only the translation, no additional text or explanations."
            
            # Use GPT-4o-mini as specified in PRD
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": text
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            st.session_state.api_usage_count += 1
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"GPT Translation Error: {str(e)}")
            return text  # Return original text on error
    
    def translate_text(self, text: str, target_language: str, context: str = "task") -> tuple[str, str]:
        """
        Hybrid translation system: Dictionary first, then GPT fallback
        Returns: (translated_text, translation_source)
        """
        if not text.strip():
            return text, 'original'
            
        # If translating to the same conceptual language, return original
        # But allow English -> English for consistency
        
        # Create cache key
        cache_key = f"{text}_{target_language}_{context}"
        
        # Check cache first
        if cache_key in st.session_state.translation_cache:
            return st.session_state.translation_cache[cache_key], 'cached'
        
        # Step 1: Try predefined dictionary
        dict_translation = self.translate_text_with_dictionary(text, target_language)
        if dict_translation and dict_translation != text:
            st.session_state.translation_cache[cache_key] = dict_translation
            return dict_translation, 'dictionary'
        
        # Step 2: Use GPT-4 fallback (even for English)
        gpt_translation = self.translate_text_with_gpt(text, target_language)
        st.session_state.translation_cache[cache_key] = gpt_translation
        return gpt_translation, 'gpt'

    
    def create_task(self, title: str, description: str, priority: str, tags: List[str] = None) -> None:
        """Create a new task"""
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            status=Status.TODO.value,
            created_at=datetime.datetime.now().isoformat(),
            tags=tags or []
        )
        st.session_state.tasks.append(task)
        st.success("✅ Task created successfully!")
    
    def update_task(self, task_id: str, **kwargs) -> None:
        """Update an existing task"""
        for i, task in enumerate(st.session_state.tasks):
            if task.id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                st.session_state.tasks[i] = task
                break
    
    def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        st.session_state.tasks = [task for task in st.session_state.tasks if task.id != task_id]
        st.success("🗑️ Task deleted successfully!")
    
    def get_filtered_tasks(self, search_query: str = "", status_filter: str = "All", priority_filter: str = "All") -> List[Task]:
        """Filter tasks based on search and filters"""
        tasks = st.session_state.tasks.copy()
        
        # Search filter
        if search_query:
            search_lower = search_query.lower()
            tasks = [
                task for task in tasks
                if search_lower in task.title.lower() 
                or search_lower in task.description.lower()
                or any(search_lower in tag.lower() for tag in task.tags)
            ]
        
        # Status filter
        if status_filter != "All":
            tasks = [task for task in tasks if task.status == status_filter]
        
        # Priority filter  
        if priority_filter != "All":
            tasks = [task for task in tasks if task.priority == priority_filter]
        
        return tasks
    
    def render_header(self):
        """Render app header with language selection"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title(self.get_ui_text('app_title'))
            st.markdown(f"*{self.get_ui_text('app_subtitle')}*")
        
        with col2:
            st.session_state.selected_language = st.selectbox(
                self.get_ui_text('language'),
                self.supported_languages,
                index=self.supported_languages.index(st.session_state.selected_language)
            )
    
    def render_task_form(self):
        """Render task creation form"""
        st.subheader(f"➕ {self.get_ui_text('add_task')}")
        
        with st.form("task_form", clear_on_submit=True):
            title = st.text_input(
                self.get_ui_text('task_title'),
                placeholder="Enter task title..."
            )
            
            description = st.text_area(
                self.get_ui_text('task_description'),
                placeholder="Enter task description...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox(
                    self.get_ui_text('priority'),
                    [p.value for p in Priority]
                )
            
            with col2:
                tags_input = st.text_input(
                    self.get_ui_text('tags'),
                    placeholder="work, urgent, personal..."
                )
            
            submitted = st.form_submit_button(f"✨ {self.get_ui_text('create_task')}")
            
            if submitted and title.strip():
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                self.create_task(title.strip(), description.strip(), priority, tags)
                st.rerun()
            elif submitted:
                st.error("Please enter a task title!")
    
    def render_task_filters(self):
        """Render search and filter controls"""
        st.subheader(f"🔍 {self.get_ui_text('search_tasks')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input(
                "🔍 Search",
                placeholder="Search tasks...",
                key="search_input"
            )
        
        with col2:
            status_filter = st.selectbox(
                self.get_ui_text('filter_by_status'),
                [self.get_ui_text('all')] + [s.value for s in Status],
                key="status_filter"
            )
        
        with col3:
            priority_filter = st.selectbox(
                self.get_ui_text('filter_by_priority'),
                [self.get_ui_text('all')] + [p.value for p in Priority],
                key="priority_filter"
            )
        
        return search_query, status_filter, priority_filter
    
    def safe_rerun(self):
        """Safely call rerun for different Streamlit versions"""
        try:
            st.rerun()  # Try new version first
        except AttributeError:
            st.experimental_rerun()

    def render_task_card(self, task: Task):
        """Render individual task card with translation"""
        current_lang = st.session_state.selected_language
        
        # Determine what to display based on current language
        if current_lang in task.translations:
            # Show translated version if available
            display_title = task.translations[current_lang].get('title', task.title)
            display_description = task.translations[current_lang].get('description', task.description)
            is_translated = True
            show_original = True
        else:
            # Show original text
            display_title = task.title
            display_description = task.description
            is_translated = False
            show_original = False
        
        # Create task card
        with st.container():
            st.markdown("---")
            
            # Task header with controls
            col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
            
            with col1:
                st.markdown(f"### {display_title}")
                if display_description:
                    st.markdown(f"*{display_description}*")
                
                # Show original text if viewing translation
                if show_original and (display_title != task.title or display_description != task.description):
                    with st.expander("📝 Original Text"):
                        st.markdown(f"**Original Title:** {task.title}")
                        if task.description:
                            st.markdown(f"**Original Description:** {task.description}")
            
            with col2:
                st.markdown(f"**{task.priority}**")
                
            with col3:
                # Status selector
                new_status = st.selectbox(
                    self.get_ui_text('status'),
                    [s.value for s in Status],
                    index=[s.value for s in Status].index(task.status),
                    key=f"status_{task.id}"
                )
                if new_status != task.status:
                    self.update_task(task.id, status=new_status)
                    self.safe_rerun()
            
            with col4:
                # Delete button
                if st.button("🗑️", key=f"delete_{task.id}", help=self.get_ui_text('delete_task')):
                    self.delete_task(task.id)
                    self.safe_rerun()
            
            # Tags display
            if task.tags:
                st.markdown("**Tags:** " + " ".join([f"`{tag}`" for tag in task.tags]))
            
            # Translation section - Always show for any language
            col1, col2, col3 = st.columns([2, 2, 4])
            
            with col1:
                # Show translate button if not already translated to current language
                if not is_translated:
                    translate_label = f"🌐 Translate to {current_lang}" if current_lang != 'English' else "🌐 Translate to English"
                    if st.button(translate_label, key=f"translate_{task.id}"):
                        with st.spinner(f"Translating to {current_lang}..."):
                            # Translate title and description
                            translated_title, source_title = self.translate_text(task.title, current_lang, "title")
                            translated_desc, source_desc = self.translate_text(task.description, current_lang, "description")
                            
                            # Store translation
                            if current_lang not in task.translations:
                                task.translations[current_lang] = {}
                            task.translations[current_lang]['title'] = translated_title
                            task.translations[current_lang]['description'] = translated_desc
                            
                            # Update task in session state
                            for i, t in enumerate(st.session_state.tasks):
                                if t.id == task.id:
                                    st.session_state.tasks[i] = task
                                    break
                        
                        self.safe_rerun()
                else:
                    # Show retranslate option
                    if st.button(f"🔄 Retranslate", key=f"retranslate_{task.id}"):
                        # Clear existing translation and retranslate
                        if current_lang in task.translations:
                            del task.translations[current_lang]
                        self.safe_rerun()
            
            with col2:
                if is_translated:
                    st.success(f"✅ Translated to {current_lang}")
        
    def render_tasks_list(self, filtered_tasks: List[Task]):
        """Render the main tasks list"""
        if not filtered_tasks:
            st.info(self.get_ui_text('no_tasks_found'))
            return
        
        # Sort tasks: Todo -> In Progress -> Completed, then by priority
        priority_order = {Priority.HIGH.value: 0, Priority.MEDIUM.value: 1, Priority.LOW.value: 2}
        status_order = {Status.TODO.value: 0, Status.IN_PROGRESS.value: 1, Status.COMPLETED.value: 2}
        
        sorted_tasks = sorted(
            filtered_tasks,
            key=lambda t: (status_order.get(t.status, 3), priority_order.get(t.priority, 3))
        )
        
        for task in sorted_tasks:
            self.render_task_card(task)
    
    def render_statistics(self):
        """Render app statistics in sidebar"""
        st.sidebar.markdown("### 📊 Statistics")
        
        total_tasks = len(st.session_state.tasks)
        completed_tasks = len([t for t in st.session_state.tasks if t.status == Status.COMPLETED.value])
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            st.sidebar.metric("Completion Rate", f"{completion_rate:.1f}%")
            st.sidebar.metric("Total Tasks", total_tasks)
            st.sidebar.metric("Completed", completed_tasks)
            st.sidebar.metric("Remaining", total_tasks - completed_tasks)
            
            # Priority breakdown
            high_priority = len([t for t in st.session_state.tasks if t.priority == Priority.HIGH.value])
            medium_priority = len([t for t in st.session_state.tasks if t.priority == Priority.MEDIUM.value])
            low_priority = len([t for t in st.session_state.tasks if t.priority == Priority.LOW.value])
            
            st.sidebar.markdown("**Priority Breakdown:**")
            st.sidebar.write(f"🔴 High: {high_priority}")
            st.sidebar.write(f"🟡 Medium: {medium_priority}") 
            st.sidebar.write(f"🟢 Low: {low_priority}")
        else:
            st.sidebar.metric("Total Tasks", 0)
        
        # Translation statistics
        st.sidebar.markdown("### 🌐 Translation Stats")
        st.sidebar.metric("API Calls Made", st.session_state.api_usage_count)
        st.sidebar.metric("Cached Translations", len(st.session_state.translation_cache))
        
        # Quick actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        if st.sidebar.button("🗑️ Clear All Tasks"):
            st.session_state.tasks = []
            st.rerun()
        
        if st.sidebar.button("🧹 Clear Translation Cache"):
            st.session_state.translation_cache = {}
            st.sidebar.success("Cache cleared!")
    
    def add_sample_tasks(self):
        """Add sample tasks for demonstration"""
        sample_tasks = [
            {
                'title': 'Buy groceries',
                'description': 'Get milk, bread, eggs and vegetables from the supermarket',
                'priority': Priority.MEDIUM.value,
                'tags': ['shopping', 'food', 'weekly']
            },
            {
                'title': 'Finish project report',
                'description': 'Complete the quarterly project analysis and submit to manager',
                'priority': Priority.HIGH.value,
                'tags': ['work', 'deadline', 'important']
            },
            {
                'title': 'Call doctor for appointment',
                'description': 'Schedule annual health checkup with family doctor',
                'priority': Priority.LOW.value,
                'tags': ['health', 'appointment', 'personal']
            },
            {
                'title': 'Pay monthly bills',
                'description': 'Pay electricity, water, internet and phone bills before due date',
                'priority': Priority.MEDIUM.value,
                'tags': ['finance', 'bills', 'monthly']
            },
            {
                'title': 'Exercise routine',
                'description': '30 minutes cardio workout at home or gym',
                'priority': Priority.LOW.value,
                'tags': ['health', 'fitness', 'daily']
            }
        ]
        
        for task_data in sample_tasks:
            self.create_task(
                title=task_data['title'],
                description=task_data['description'],
                priority=task_data['priority'],
                tags=task_data['tags']
            )
    
    def export_tasks_json(self) -> str:
        """Export all tasks to JSON format"""
        tasks_data = []
        for task in st.session_state.tasks:
            task_dict = asdict(task)
            tasks_data.append(task_dict)
        
        return json.dumps(tasks_data, indent=2, ensure_ascii=False)
    
    def import_tasks_json(self, json_data: str) -> bool:
        """Import tasks from JSON data"""
        try:
            tasks_data = json.loads(json_data)
            imported_count = 0
            
            for task_data in tasks_data:
                # Create task object
                task = Task(
                    id=task_data.get('id', str(uuid.uuid4())),
                    title=task_data['title'],
                    description=task_data['description'],
                    priority=task_data['priority'],
                    status=task_data['status'],
                    created_at=task_data['created_at'],
                    tags=task_data.get('tags', []),
                    translations=task_data.get('translations', {})
                )
                st.session_state.tasks.append(task)
                imported_count += 1
            
            st.success(f"✅ Successfully imported {imported_count} tasks!")
            return True
            
        except Exception as e:
            st.error(f"❌ Import failed: {str(e)}")
            return False
    
    def run(self):
        """Main application entry point"""
        # Page configuration
        st.set_page_config(
            page_title="AI Todo App",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .task-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: #fafafa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Render sidebar statistics and quick actions
        self.render_statistics()
        
        # Add sample data button in sidebar
        if st.sidebar.button("📝 Add Sample Tasks"):
            if not st.session_state.tasks:
                self.add_sample_tasks()
                st.rerun()
            else:
                st.sidebar.warning("Tasks already exist. Clear all tasks first.")
        
        
        # Main app header
        self.render_header()
        
        # Create main tabs
        tab1, tab2, tab3 = st.tabs(["➕ Create Task", "📋 Manage Tasks", "📊 Analytics"])
        
        with tab1:
            self.render_task_form()
            
            # Show recent tasks preview
            if st.session_state.tasks:
                st.markdown("### 👀 Recent Tasks Preview")
                recent_tasks = sorted(st.session_state.tasks, key=lambda x: x.created_at, reverse=True)[:3]
                for task in recent_tasks:
                    with st.expander(f"{task.priority} {task.title}"):
                        st.write(f"**Description:** {task.description}")
                        st.write(f"**Status:** {task.status}")
                        if task.tags:
                            st.write(f"**Tags:** {', '.join(task.tags)}")
        
        with tab2:
            search_query, status_filter, priority_filter = self.render_task_filters()
            
            # Convert "All" back to English for filtering logic
            if status_filter == self.get_ui_text('all'):
                status_filter = "All"
            if priority_filter == self.get_ui_text('all'):
                priority_filter = "All"
            
            filtered_tasks = self.get_filtered_tasks(search_query, status_filter, priority_filter)
            
            # Show task count
            st.markdown(f"### 📋 Tasks ({len(filtered_tasks)} of {len(st.session_state.tasks)})")
            
            self.render_tasks_list(filtered_tasks)
        
        with tab3:
            self.render_analytics_dashboard()
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 0.8em; padding: 1rem;'>
                🤖 AI Todo App - Intelligent Multilingual Task Management<br>
                Built with Streamlit • Supports 6 Languages: English, Spanish, French, German, Italian, Hindi<br>
                Hybrid Translation: Dictionary + GPT-4 Fallback
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    def render_analytics_dashboard(self):
        """Render analytics and insights dashboard"""
        st.subheader("📊 Analytics Dashboard")
        
        if not st.session_state.tasks:
            st.info("No tasks available for analytics. Create some tasks first!")
            return
        
        # Key metrics
        total_tasks = len(st.session_state.tasks)
        completed_tasks = len([t for t in st.session_state.tasks if t.status == Status.COMPLETED.value])
        in_progress_tasks = len([t for t in st.session_state.tasks if t.status == Status.IN_PROGRESS.value])
        todo_tasks = len([t for t in st.session_state.tasks if t.status == Status.TODO.value])
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Tasks", total_tasks)
        with col2:
            st.metric("✅ Completed", completed_tasks)
        with col3:
            st.metric("⏳ In Progress", in_progress_tasks)
        with col4:
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.metric("📈 Completion Rate", f"{completion_rate:.1f}%")
        
        # Priority and Status breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Priority Breakdown")
            high_priority = len([t for t in st.session_state.tasks if t.priority == Priority.HIGH.value])
            medium_priority = len([t for t in st.session_state.tasks if t.priority == Priority.MEDIUM.value])
            low_priority = len([t for t in st.session_state.tasks if t.priority == Priority.LOW.value])
            
            priority_data = {
                "🔴 High": high_priority,
                "🟡 Medium": medium_priority,
                "🟢 Low": low_priority
            }
            
            for priority, count in priority_data.items():
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                st.write(f"{priority}: {count} ({percentage:.1f}%)")
        
        with col2:
            st.markdown("#### 📊 Status Breakdown") 
            status_data = {
                "📝 Todo": todo_tasks,
                "⏳ In Progress": in_progress_tasks,
                "✅ Completed": completed_tasks
            }
            
            for status, count in status_data.items():
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                st.write(f"{status}: {count} ({percentage:.1f}%)")
        
        # Translation statistics
        st.markdown("#### 🌐 Translation Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔄 API Calls Made", st.session_state.api_usage_count)
        with col2:
            st.metric("💾 Cached Translations", len(st.session_state.translation_cache))
        with col3:
            translated_tasks = len([t for t in st.session_state.tasks if t.translations])
            st.metric("🌍 Translated Tasks", translated_tasks)
        
        # Most used tags
        if any(task.tags for task in st.session_state.tasks):
            st.markdown("#### 🏷️ Popular Tags")
            all_tags = []
            for task in st.session_state.tasks:
                all_tags.extend(task.tags)
            
            from collections import Counter
            tag_counts = Counter(all_tags)
            
            if tag_counts:
                for tag, count in tag_counts.most_common(5):
                    st.write(f"`{tag}`: {count} tasks")

# Main application execution
def main():
    """Main function to run the app"""
    try:
        app = AITodoApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()