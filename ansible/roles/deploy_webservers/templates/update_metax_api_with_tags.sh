if [ "$#" -ne 1 ]
then
  echo "Give exactly one tag name for metax-api"
  echo "Example: '$0 v0.1.0'"
  exit 2
fi

if [ "$USER" != "{{ app_user }}" ]; then
    echo "Run this as {{ app_user }}"
    su {{ app_user }}
fi

source {{ python_virtualenv_path }}/bin/activate
cd {{ metax_app_base_path }}

git fetch --all --tags --prune && git checkout $1
