mkdir -f trash

for i in {1..520}
  do
  #echo $i
  wget "https://apps.odoo.com/apps/modules/browse/page/$i?price=Paid" -O trash/Page"$i".html
done

cat trash/Page*.html | grep -o 'href="/apps/modules/[0-9.]\+/[^"]\+"' | grep -o '/[^"]\+' | sort -u | tee all_apps_urls.txt
echo "Total `wc -l all_apps_urls.txt` apps"

