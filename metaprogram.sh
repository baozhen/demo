#!/bin/bash
# metaprogram
echo '#!/bin/bash' >program
for ((I=1; I<=922; I++)) do
    echo "echo $I" >>program
done
chmod +x program
