mkdir -f trash

for i in {1..520}
  do
  #echo $i
  wget "https://apps.odoo.com/apps/modules/browse/page/$i?price=Paid" -O trash/Page"$i".html
done

cat trash/Page*.html | grep -o 'href="/apps/modules/[0-9.]\+/[^"]\+"' | grep -o '/[^"]\+' | sort -u | tee all_apps_urls.txt
echo "Total `wc -l all_apps_urls.txt` apps"

# Prepend URL start:
sed -e "s/^/https:\/\/apps.odoo.com/" all_apps_urls.txt > trash/tmp5.txt
mv trash/tmp5.txt all_apps_urls.txt

# Getting all modules pages:
for modurl in `cat all_apps_urls.txt`
do
    echo wget "$modurl" -O trash/mod_named_"`printf '%s' "$modurl" | grep -o '[^/]\+$'`"_page.html
done > trash/modpage_getting_script.bash

# Separate in batches for parallel exec:
sed -n -e "0~5p" trash/modpage_getting_script.bash > trash/modpage_getting_script_batch0.bash
sed -n -e "1~5p" trash/modpage_getting_script.bash > trash/modpage_getting_script_batch1.bash
sed -n -e "2~5p" trash/modpage_getting_script.bash > trash/modpage_getting_script_batch2.bash
sed -n -e "3~5p" trash/modpage_getting_script.bash > trash/modpage_getting_script_batch3.bash
sed -n -e "4~5p" trash/modpage_getting_script.bash > trash/modpage_getting_script_batch4.bash

#bash trash/modpage_getting_script.bash
#grep '<td><b>License</b></td>' trash/mod_named_dev_payslip_batches_page.html

