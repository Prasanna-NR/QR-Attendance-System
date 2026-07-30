// QR Attendance System - JavaScript Functions

$(document).ready(function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);

    // Form validation
    $('form').on('submit', function(e) {
        let isValid = true;
        $(this).find('input[required], textarea[required], select[required]').each(function() {
            if (!$(this).val().trim()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        if (!isValid) {
            e.preventDefault();
            alert('Please fill all required fields.');
        }
    });

    // Password strength indicator
    $('#password').on('keyup', function() {
        const password = $(this).val();
        const strength = getPasswordStrength(password);
        const indicator = $('#password-strength');
        
        if (indicator.length) {
            indicator.removeClass('bg-danger bg-warning bg-success');
            if (strength === 'weak') {
                indicator.addClass('bg-danger').text('Weak');
            } else if (strength === 'medium') {
                indicator.addClass('bg-warning').text('Medium');
            } else if (strength === 'strong') {
                indicator.addClass('bg-success').text('Strong');
            } else {
                indicator.text('');
            }
        }
    });

    // QR Scanner - check camera availability
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                stream.getTracks().forEach(track => track.stop());
                // Camera available
            })
            .catch(function(error) {
                // Camera not available - show fallback option
                $('#scanner-container').html(`
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Camera not detected. You can upload an image with QR code instead.
                    </div>
                `);
            });
    }
});

function getPasswordStrength(password) {
    if (password.length < 6) return 'weak';
    if (password.length < 10) return 'medium';
    if (password.length >= 10 && /\d/.test(password) && /[a-z]/.test(password) && /[A-Z]/.test(password)) {
        return 'strong';
    }
    return 'medium';
}

// Copy QR code to clipboard
function copyQRCode(element) {
    const qrImg = document.querySelector(element);
    if (qrImg) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = function() {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            canvas.toBlob(function(blob) {
                navigator.clipboard.write([
                    new ClipboardItem({
                        [blob.type]: blob
                    })
                ]).then(function() {
                    showNotification('QR Code copied to clipboard!', 'success');
                }).catch(function() {
                    showNotification('Failed to copy QR Code', 'danger');
                });
            });
        };
        img.src = qrImg.src;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show notification-toast">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $('body').append(alertHtml);
    setTimeout(function() {
        $('.notification-toast').alert('close');
    }, 3000);
}

// Export data to CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (const row of rows) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        for (const col of cols) {
            rowData.push(col.innerText.trim());
        }
        csv.push(rowData.join(','));
    }
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Task management functions
function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        $.ajax({
            url: `/task/${taskId}/delete`,
            type: 'POST',
            success: function() {
                location.reload();
            },
            error: function() {
                alert('Error deleting task');
            }
        });
    }
}

function completeTask(taskId) {
    $.ajax({
        url: `/task/${taskId}/complete`,
        type: 'POST',
        success: function() {
            location.reload();
        },
        error: function() {
            alert('Error completing task');
        }
    });
}