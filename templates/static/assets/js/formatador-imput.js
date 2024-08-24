document.addEventListener('DOMContentLoaded', () => {
    console.log('Script carregado e executado')

    function formatField(inputElement, format) {
        if (inputElement) {
            inputElement.addEventListener('input', function () {
                let value = this.value.replace(/\D/g, '') // Remove todos os caracteres não numéricos
                let formattedValue = ''

                for (let i = 0; i < format.length && value.length > 0; i++) {
                    if (format[i] === '#') {
                        formattedValue += value[0]
                        value = value.slice(1)
                    } else {
                        formattedValue += format[i]
                    }
                }

                this.value = formattedValue
            })
        }
    }

    // Usando a função formatField para formatar os campos
    formatField(document.getElementById('cep'), '#####-####')
    formatField(document.getElementById('id_cep'), '#####-####')
    formatField(document.getElementById('id_telefone'), '(##) #####-####')
})
