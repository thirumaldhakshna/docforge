def get_stylesheet():
    return """
    /* Global Settings */
    QMainWindow {
        background-color: #1E1E1E;
        font-family: 'Segoe UI', Inter, Roboto, sans-serif;
        color: #FFFFFF;
    }
    
    #mainWindowFrame {
        background-color: #1E1E1E;
        border-top: 1px solid #3E3E42;
        border-left: 1px solid #3E3E42;
        border-right: 1px solid #3E3E42;
        border-bottom: 1px solid #3E3E42;
    }
    
    QWidget {
        font-family: 'Segoe UI', Inter, Roboto, sans-serif;
        color: #FFFFFF;
    }

    /* Custom Title Bar */
    #customTitleBar {
        background-color: #1E1E1E;
    }
    QPushButton#titleBarBtn, QPushButton#titleBarCloseBtn {
        background-color: transparent;
        border: none;
        color: #CCCCCC;
        font-size: 14px;
        min-width: 46px;
        max-width: 46px;
        min-height: 32px;
        max-height: 32px;
        padding: 0;
        margin: 0;
        border-radius: 0;
    }
    QPushButton#titleBarBtn:hover {
        background-color: #37373D;
    }
    QPushButton#titleBarCloseBtn:hover {
        background-color: #E81123;
        color: white;
    }

    /* Cards / Sections (Flattened) */
    QWidget[class="CardWidget"] {
        background-color: transparent;
        border: none;
    }

    QLabel[class="CardTitle"] {
        font-weight: 700;
        font-size: 11px;
        letter-spacing: 1px;
        color: #A0A0A0;
        padding: 0;
    }

    QLabel[class="FieldGroupTitle"] {
        font-weight: 700;
        font-size: 10px;
        letter-spacing: 0.8px;
        color: #A0A0A0;
        padding: 0;
    }

    /* Panels */
    #leftPanelContainer {
        background-color: #202225;
        border-top: 0px;
        border-left: 0px;
        border-bottom: 0px;
        border-right: 1px solid #3E3E42;
    }
    #rightPanelContainer {
        background-color: #202225;
        border-left: 1px solid #3E3E42;
    }

    /* Center Panel & Canvas */
    #centerPanel {
        background-color: #1E1E1E;
        border-top: 0px;
        border-left: 0px;
        border-bottom: 0px;
        border-right: 0px;
    }
    
    QSplitter::handle {
        background-color: #3E3E42;
    }
    
    #canvasArea {
        background-color: #1E1E1E;
    }
    
    #canvasContainer {
        background-color: #2D2D30;
        border: none;
    }

    /* Top Navigation */
    #topNav {
        background-color: #1E1E1E;
        border-top: 0px;
        border-left: 0px;
        border-right: 0px;
        border-bottom: 1px solid #3E3E42;
    }
    
    #appLogo {
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 1px;
    }

    /* Mode Switching Buttons */
    QPushButton[class="navButton"] {
        background-color: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0px;
        padding: 8px 20px;
        font-size: 13px;
        color: #BDBDBD;
    }
    
    QPushButton[class="navButton"]:hover {
        color: #FFFFFF;
        background-color: #252526;
    }
    
    QPushButton[class="navButton"]:checked {
        color: #FFFFFF;
        border-bottom: 2px solid #007ACC;
    }

    /* Buttons */
    QPushButton[class="primaryButton"] {
        background-color: #007ACC;
        color: #FFFFFF;
        border-radius: 4px;
        padding: 0 14px;
        border: 1px solid #007ACC;
        min-height: 32px;
        font-weight: 600;
    }
    QPushButton[class="primaryButton"]:hover {
        background-color: #005A9E;
        border: 1px solid #005A9E;
    }
    
    QPushButton[class="secondaryButton"] {
        background-color: #3E3E42;
        color: #FFFFFF;
        border: 1px solid #454545;
        border-radius: 4px;
        padding: 0 12px;
        min-height: 32px;
    }
    QPushButton[class="secondaryButton"]:hover {
        background-color: #4D4D50;
    }
    
    QPushButton[class="secondaryButton"]:checked {
        background-color: #007ACC;
        border: 1px solid #007ACC;
    }

    /* Toolbar / Icon Buttons */
    QToolBar {
        background-color: #252526;
        border-bottom: 1px solid #3E3E42;
        spacing: 4px;
        padding: 8px 12px;
    }
    
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        min-width: 32px;
        min-height: 32px;
        max-width: 32px;
        max-height: 32px;
        padding: 4px;
        color: #D4D4D4;
    }
    
    QToolButton:hover {
        background-color: #3A3D41;
        color: #FFFFFF;
        border-radius: 4px;
    }
    
    QToolButton:pressed, QToolButton:checked {
        background-color: #4A4D52;
        color: #FFFFFF;
        border: 1px solid #5A5D62;
        border-radius: 4px;
    }

    /* Radio Buttons */
    QRadioButton {
        color: #CCCCCC;
        spacing: 8px;
        min-height: 22px;
    }
    QRadioButton::indicator {
        width: 14px;
        height: 14px;
        border-radius: 8px;
        border: 1px solid #FFFFFF;
        background-color: transparent;
    }
    QRadioButton::indicator:checked {
        width: 8px;
        height: 8px;
        border-radius: 8px;
        border: 4px solid #007ACC;
        background-color: #1E1E1E;
    }
    QRadioButton:disabled {
        color: #666666;
    }
    QRadioButton::indicator:disabled {
        border: 2px solid #666666;
    }

    /* Inputs & Comboboxes */
    QLineEdit, QComboBox {
        border: 1px solid #3E3E42;
        border-radius: 4px;
        padding: 0 10px;
        background-color: #3C3C3C;
        color: #CCCCCC;
        min-height: 30px;
    }
    
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #007ACC;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView {
        background-color: #252526;
        border: 1px solid #3E3E42;
        color: #CCCCCC;
        selection-background-color: #007ACC;
    }

    /* Lists */
    QListWidget {
        border: 1px solid #3E3E42;
        background-color: #1E1E1E;
        color: #CCCCCC;
        border-radius: 4px;
        outline: none;
    }
    
    QListWidget::item {
        padding: 6px 10px;
        border: none;
        margin: 3px 4px;
        border-radius: 4px;
        background-color: #2A2D2E;
    }
    
    QListWidget::item:hover {
        background-color: #2A2D2E;
    }
    
    QListWidget::item:selected {
        background-color: #04395E;
        color: #FFFFFF;
    }

    /* Empty States */
    QLabel[class="emptyState"] {
        color: #CCCCCC;
        font-size: 14px;
        font-weight: 600;
        padding: 4px;
    }

    QLabel[class="emptyStateSubtle"] {
        color: #858585;
        font-size: 12px;
        padding: 0;
    }

    QLabel[class="emptyStateIcon"] {
        padding: 0 0 8px 0;
    }

    QFrame#rightSectionDivider {
        background-color: #3E3E42;
        border: none;
        min-height: 1px;
        max-height: 1px;
    }

    QFrame#exportConfigPanel {
        background-color: #252526;
        border: 1px solid #3E3E42;
        border-radius: 4px;
    }

    QWidget#statusBarWidget {
        background-color: #007ACC;
        border-top: 1px solid #0E639C;
    }

    QLabel#statusBarLabel {
        color: #FFFFFF;
        font-size: 12px;
        padding: 0 10px;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: 1px solid #3E3E42;
        background-color: #1E1E1E;
        border-radius: 2px;
        height: 6px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #007ACC;
        border-radius: 2px;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #007ACC;
        color: #FFFFFF;
    }
    QStatusBar QLabel {
        color: #FFFFFF;
        padding: 0 8px;
    }

    /* Menus */
    QMenuBar {
        background-color: #1E1E1E;
        color: #CCCCCC;
        border: none;
    }
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }
    QMenuBar::item:selected {
        background-color: #094771;
        color: white;
    }
    QMenuBar::item:hover {
        background-color: #3E3E42;
    }
    
    QMenu {
        background-color: #252526;
        color: white;
        border: 1px solid #3E3E42;
    }
    QMenu::item {
        padding: 8px 24px;
        background: transparent;
    }
    QMenu::item:selected {
        background-color: #094771;
        color: white;
    }
    QMenu::separator {
        height: 1px;
        background: #3E3E42;
        margin: 4px 0;
    }
    
    /* Custom Dialog */
    #customDialogContainer {
        border-top: 1px solid #3E3E42;
        border-left: 1px solid #3E3E42;
        border-right: 1px solid #3E3E42;
        border-bottom: 1px solid #3E3E42;
    }
    #customDialogTitleBar {
        background-color: #1E1E1E;
        border-top: 0px;
        border-left: 0px;
        border-right: 0px;
        border-bottom: 1px solid #2D2D30;
    }
    #customDialogTitle {
        color: white;
        font-size: 13px;
    }
    #customDialogBody {
        background-color: #252526;
    }
    #customDialogText {
        color: white;
        font-size: 13px;
    }
    QPushButton#customDialogCloseBtn {
        background-color: transparent;
        border: none;
        color: white;
        font-size: 14px;
        min-width: 46px;
        max-width: 46px;
        min-height: 30px;
        max-height: 30px;
        padding: 0;
        margin: 0;
        border-radius: 0;
    }
    QPushButton#customDialogCloseBtn:hover {
        background-color: #E81123;
    }
    QPushButton#customDialogBtn {
        background-color: #3C3C3C;
        color: white;
        border: 1px solid #555555;
        min-width: 90px;
        padding: 6px;
        border-radius: 4px;
    }
    QPushButton#customDialogBtn:hover {
        background-color: #4A4A4A;
    }
    QPushButton#customDialogBtn:pressed {
        background-color: #007ACC;
    }
    """
