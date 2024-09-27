replace="io.github.philippkosarev.bmi"
with="io.github.philippkosarev.bmi"

# Renaming files
echo renaming files
FILES=$(ls -R | grep $replace)
for FILE in $FILES
do
  FILE=$(find -name $FILE)
  EDITEDFILE="$(echo $FILE | sed "s|$replace|$with|")"
  git mv $FILE $EDITEDFILE
done

# Find and replace inside each file
echo replacing text inside files
grep -rl $replace . | xargs sed -i "s|$replace|$with|g"
