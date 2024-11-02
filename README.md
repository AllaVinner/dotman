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
An intrinsic part of `dotman` is the **dotman project**, or simply project.
A project is any folder with a dotman configuration file, i.e. `.dotman.json`.
When a link is added, see [Add](#add), the original file or folder is moved to the project 
folder and an entry in the configuration file is added.
Finally, a symlink is created where the orifinal object previously recided.

The link entry in the configuration file keeps the link path as relative to your home path,
and the target is stored as the name of the moved file.
This means that it is possible to move a dotman project, call `dotman restore`, and have it working again.


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









