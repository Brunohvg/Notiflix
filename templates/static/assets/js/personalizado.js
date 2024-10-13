document.addEventListener('DOMContentLoaded', () => {
    console.log('Script carregado e executado');

    // Função para formatar campos de entrada
    function formatField(inputElement, format) {
        if (inputElement) {
            inputElement.addEventListener('input', function () {
                let value = this.value.replace(/\D/g, ''); // Remove todos os caracteres não numéricos
                let formattedValue = '';

                for (let i = 0; i < format.length && value.length > 0; i++) {
                    if (format[i] === '#') {
                        formattedValue += value[0];
                        value = value.slice(1);
                    } else {
                        formattedValue += format[i];
                    }
                }

                this.value = formattedValue;
            });
        }
    }

    // Usando a função formatField para formatar os campos
    formatField(document.getElementById('cep'), '#####-####');
    formatField(document.getElementById('id_cep'), '#####-####');
    formatField(document.getElementById('id_telefone'), '(##) #####-####');

    // Seleciona todos os alertas e aplica fade
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 500); // Tempo para a animação de fade
        }, 2000); // Tempo antes do fade
    });

    // Função para mudar a cor de fundo de um elemento
    function changeBackgroundColor(elementId, color, duration) {
        const element = document.getElementById(elementId);
        if (element) {
            setTimeout(() => {
                element.style.backgroundColor = color;
            }, duration);
        }
    }

    // Chamando a função para mudar a cor de fundo
    changeBackgroundColor('elementoId', 'lightblue', 3000); // Altera a cor para lightblue após 3 segundos

    // Ajuste de altura para os textareas
    const textareas = document.querySelectorAll("textarea.form-control");

    function adjustTextareaHeights() {
        // Reseta a altura de todos os textareas
        textareas.forEach(textarea => {
            textarea.style.height = "auto"; 
        });

        // Encontra a altura máxima
        let maxHeight = 0;
        textareas.forEach(textarea => {
            maxHeight = Math.max(maxHeight, textarea.scrollHeight);
        });

        // Define a altura máxima para todos os textareas
        textareas.forEach(textarea => {
            textarea.style.height = maxHeight + "px"; 
        });
    }

    textareas.forEach(textarea => {
        textarea.addEventListener("input", adjustTextareaHeights);
    });

    // Disparar o evento ao carregar a página
    adjustTextareaHeights();

    // ==============================
    // Adicionando Novo Código Aqui
    // ==============================

});
