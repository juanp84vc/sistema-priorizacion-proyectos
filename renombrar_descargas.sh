#!/bin/bash
# Script para renombrar archivos descargados sin extensión

echo "🔧 Renombrando archivos descargados..."
echo ""

cd ~/Downloads

# Contador
count=0

# Renombrar archivos sin extensión que vienen de localhost:8501
for file in *; do
    # Solo procesar archivos (no directorios)
    if [ -f "$file" ]; then
        # Verificar si el archivo no tiene extensión (no contiene punto)
        if [[ ! "$file" =~ \. ]]; then
            # Detectar tipo de archivo
            file_type=$(file -b "$file")
            
            # Determinar extensión basada en el tipo
            if [[ "$file_type" == *"Microsoft OOXML"* ]] || [[ "$file_type" == *"Word"* ]]; then
                new_name="proyecto_${count}_evaluacion.docx"
                mv "$file" "$new_name"
                echo "✅ $file → $new_name (Word)"
                ((count++))
            elif [[ "$file_type" == *"PDF"* ]]; then
                new_name="proyecto_${count}_evaluacion.pdf"
                mv "$file" "$new_name"
                echo "✅ $file → $new_name (PDF)"
                ((count++))
            elif [[ "$file_type" == *"Excel"* ]] || [[ "$file_type" == *"Zip"* ]]; then
                new_name="proyecto_${count}_evaluacion.xlsx"
                mv "$file" "$new_name"
                echo "✅ $file → $new_name (Excel)"
                ((count++))
            fi
        fi
    fi
done

echo ""
if [ $count -eq 0 ]; then
    echo "ℹ️  No se encontraron archivos sin extensión para renombrar"
else
    echo "✅ Se renombraron $count archivos"
    echo ""
    echo "📁 Archivos renombrados en ~/Downloads:"
    ls -lh ~/Downloads/proyecto_*_evaluacion.* 2>/dev/null | tail -10
fi

echo ""
echo "💡 Ahora puedes abrir los archivos con:"
echo "   open ~/Downloads/proyecto_0_evaluacion.docx"
echo "   open ~/Downloads/proyecto_0_evaluacion.pdf"
echo "   open ~/Downloads/proyecto_0_evaluacion.xlsx"
