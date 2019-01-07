# Biology: https://www.unb.ca/fredericton/science/depts/biology/people/index.html

lynx -dump -listonly -nonumbers $1  | grep phonebook | awk '{gsub("?dn=","?vcard=",$1);print $1}' > vcards.html
rm -f list.txt missing_vcards.txt
count=1
for l in `cat vcards.html`
do
  echo -n "Reading vcard $count\r"
  curl -s $l > vcard
  if ! grep "TITLE:" vcard > /dev/null
    then
    echo "$count" >> missing_vcards.txt
  fi
  grep "TITLE:" vcard | awk '{gsub("TITLE:"," ",$0);print $0}' | dos2unix  | tr '\n' , | awk '{gsub(/,$/,""); print}' > title
  grep "FN:" vcard | awk '{gsub("FN:","",$0);print $0}' | dos2unix > name
  grep "EMAIL;" vcard | awk '{gsub("EMAIL;TYPE=INTERNET:","",$0);print $0}' | dos2unix > email
  echo "$count" | tr -d '\n' > count
  paste -d ';' count name email title >> list.txt
  count=$((count+1))
done
rm -f vcard count name email title vcards.html
