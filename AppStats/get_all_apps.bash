for i in {1..520}
  do
  #echo $i
  wget "https://apps.odoo.com/apps/modules/browse/page/$i?price=Paid" -O Page"$i".html
done


cat Page*.html | grep -o 'href="/apps/modules/[0-9.]\+/[^"]\+"' | tee all_apps_urls.txt

