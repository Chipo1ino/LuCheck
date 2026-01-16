document.addEventListener('DOMContentLoaded', function() {
    const folderInput = document.getElementById('folderInput');
    const selectedFolderInput = document.getElementById('selectedFolder');
    const archiveNameInput = document.getElementById('archiveName');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const selectFolderBtn = document.getElementById('selectFolderBtn');
    const createArchiveBtn = document.getElementById('createArchiveBtn');
    const statusMessage = document.getElementById('statusMessage');
    
    let selectedFiles = [];

    selectFolderBtn.addEventListener('click', () => folderInput.click());
    selectedFolderInput.addEventListener('click', () => folderInput.click());
    
    folderInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            selectedFiles = Array.from(e.target.files);
            const folderName = getFolderNameFromFiles(selectedFiles);
            selectedFolderInput.value = folderName;
            
            if (!archiveNameInput.value || archiveNameInput.value === 'backup.7z') {
                archiveNameInput.value = `${folderName}.7z`;
            }
            if (selectedFiles.length == 0) {
                showMessage(`Загружена пустая папка!`)
            }
            showMessage(`Выбрано файлов: ${selectedFiles.length} из папки "${folderName}"`, 'success');
            createArchiveBtn.disabled = false;
        }
    });
    
    function getFolderNameFromFiles(files) {
        if (files.length === 0) return '';
        const firstFile = files[0];
        if (firstFile.webkitRelativePath) {
            return firstFile.webkitRelativePath.split('/')[0];
        }
        return 'selected_folder';
    }
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.innerHTML = type === 'password' ? 
            '<i class="fas fa-eye"></i>' : 
            '<i class="fas fa-eye-slash"></i>';
    });
    createArchiveBtn.addEventListener('click', async function() {
        const archiveName = archiveNameInput.value.trim();
        const password = passwordInput.value.trim() || null;
        
        if (selectedFiles.length === 0) {
            showMessage('Сначала выберите папку', 'danger');
            return;
        }
        
        if (!archiveName) {
            showMessage('Введите имя архива', 'danger');
            archiveNameInput.focus();
            return;
        }
        const originalText = createArchiveBtn.innerHTML;
        createArchiveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Создание архива...';
        createArchiveBtn.disabled = true;
        
        try {
            const response = await fetch('/api/create-archive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    folderPath: selectedFolderInput.value,
                    archiveName: archiveName,
                    password: password
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(result.message, 'success');
                
                // Скачиваем архив
                setTimeout(() => {
                    window.location.href = result.downloadUrl;
                }, 1000);
            } else {
                showMessage(`Ошибка: ${result.error}`, 'danger');
            }
        } catch (error) {
            showMessage(`Ошибка соединения: ${error.message}`, 'danger');
        } finally {
            createArchiveBtn.innerHTML = originalText;
            createArchiveBtn.disabled = false;
        }
    });
    
    // Показать сообщение
    function showMessage(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `alert alert-${type}`;
        statusMessage.style.display = 'block';
        
        // Автоматически скрыть через 5 секунд
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 5000);
    }
    
    // Enter для создания архива
    archiveNameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !createArchiveBtn.disabled) {
            createArchiveBtn.click();
        }
    });
    
    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !createArchiveBtn.disabled) {
            createArchiveBtn.click();
        }
    });
    
});