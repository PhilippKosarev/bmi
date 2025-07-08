<h1>BMI</h1>

BMI is an open-source, body mass index calculator built with GTK4 and LibAdwaita.

<img width='640' alt='Download on Flathub' src='screenshots/simple-dark.png'/>

<p>
<h1>Installing</h2>
<p>
Available on <a href='https://flathub.org/apps/details/io.github.philippkosarev.bmi'>Flathub</a>.
</a>
<p>
<a href='https://flathub.org/apps/details/io.github.philippkosarev.bmi'>
<img width='176' alt='Download on Flathub' src='https://flathub.org/api/badge?locale=en' />
</a>
</p>
and via <a href='https://github.com/PhilippKosarev/bmi/releases'>Github Releases</a>.
</p>

<p>
<h1>Building</h2>
This project is built using <a href='https://apps.gnome.org/en-GB/Builder'>Gnome Builder</a>.

You can also manually run the meson commands to install and run the app natively.
<pre>
meson setup build
cd build
meson compile
meson install
bmi
ninja uninstall
</pre>
or just run <code>./run.sh</code> which does that for you.
</p>
