# DOTMAN
A simple CLI or python script for managing dotfiles.

- **Init** a new dotman dotfile project
```
dotman init ./dotfileproject
```

- **Add** an existing dotfile to a dotfile project
```
dotman add ~/.basrc ./dotfileproject
```

- **Restore** a dotfile project on a new machine
```
dotman restore ./dotfileproject
```

## How It Works
A dotman project is any folder containing a `.dotman.json` file.
When a link is added, see [Add](#add), the original file or folder is moved to the project, 
an entry in the configuration file is added, and 
a symlink from the original to the moved object is created.

The link entry in the configuration file saves the link path as relative to your home path,
and the target is stored as the name of the moved file.
This means that it is possible to move a dotman project, and 
then restoring it using `dotman restore`.


## Example

**Original Folder Structure**
```
~
├── .bashrc
└── dotfiles
```

```bash
dotman init ~/dotfiles/bash`
```

```
~
├── .bashrc
└── dotfiles
    └── bash
        └── .dotman.json # {links: {}}
```

```bash
dotman add ~/.bashrc ~/dotfiles/bash`
```

```
~
├── .bashrc -> ~/dotfiles/bash/.bashrc
└── dotfiles
    └── bash
        ├── .bashrc
        └── .dotman.json # {"links": {".bashrc": ".bashrc"}}
```

```bash
rm ~/.bashrc
mv ~/dotfiles ~/configs
```

```
~
└── configs
    └── bash
        ├── .bashrc
        └── .dotman.json # {"links": {".bashrc": ".bashrc"}}
```

```bash
dotman restore ~/configs/bash
```

```
~
├── .bashrc -> ~/configs/bash/.bashrc
└── configs
    └── bash
        ├── .bashrc
        └── .dotman.json # {"links": {".bashrc": ".bashrc"}}
```


## Commands

### Add

## As Module
`python -m dotman`

## Similar Projects

https://github.com/SuperCuber/dotter
https://github.com/jbernard/dotfiles









