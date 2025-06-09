# ClusterWebLab 🧪✨

**Advanced Molecular Cluster Analysis Platform**

ClusterWebLab is a comprehensive web application designed for visualizing, generating, and optimizing molecular structures in XYZ format. Built with modern technologies including **Flask** for the backend and **3Dmol.js** for interactive 3D visualization, it provides researchers and students with powerful tools for molecular analysis.

---

## 🌐 Live Demo

Experience the platform live at: **[https://clusterweblab.appx.ro/](https://clusterweblab.appx.ro/)**

---

## ✨ Key Features

### 🧬 **3D Molecular Visualization**
- Interactive 3D viewer powered by 3Dmol.js
- Real-time structure manipulation and rotation
- High-quality molecular rendering with customizable styles

### 🔗 **Intelligent Cluster Generation**
- Generate random molecular clusters with specified atomic compositions
- Support for transition metals (Fe, Co, Ni) and noble metals (Cu, Pd, Ag, Pt, Au)
- Customizable cluster formulas (e.g., Pd12Pt1, Au13, CuPd8)

### ⚙️ **Advanced Structure Optimization**
- Multiple optimization algorithms:
  - **L-BFGS-B**: Fast local minimum search
  - **Basin-Hopping**: Global minimum exploration
- Real-time energy calculations and performance metrics
- Automatic structure comparison (before/after optimization)

### 🎨 **Customizable Visualization**
- Multiple color schemes (Jmol, Rasmol)
- Dark/Light theme support
- Responsive design for all devices

### 📂 **File Management System**
- Drag-and-drop XYZ file upload
- Export optimized structures as XYZ files
- High-resolution PNG image export
- Secure user session management

### 🔔 **Smart Notification System**
- Real-time feedback for all operations
- Auto-dismissing notifications
- Error handling with detailed messages

---

## 🛠️ System Requirements

### **Minimum Requirements**
- **Python**: 3.9 or higher 🐍
- **Memory**: 2GB RAM minimum
- **Storage**: 500MB free space
- **Browser**: Modern web browser with JavaScript ES6+ support

### **Recommended**
- **Python**: 3.11+
- **Memory**: 4GB RAM
- **CPU**: Multi-core processor for faster optimizations

---

## 📦 Installation & Setup

### **1. Clone Repository**
```bash
git clone https://github.com/arturylab/clusterWebLab.git
cd clusterWebLab
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run Application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## 📋 Python Dependencies

```
Flask>=2.3.0
APScheduler>=3.10.0
numpy>=1.24.0
scipy>=1.10.0
ase>=3.22.0
```

---

## 🚀 Quick Start Guide

### **Upload & Visualize**
1. Launch the application
2. Drag and drop your XYZ file into the upload area
3. The structure will automatically load in the 3D viewer

### **Generate Random Clusters**
1. Enter a cluster formula (e.g., `Pd12Pt1`)
2. Click "Generate Structure"
3. View the randomly generated cluster

### **Optimize Structures**
1. Load or generate a molecular structure
2. Select optimization method (L-BFGS-B or Basin-Hopping)
3. Click "Optimize Structure"
4. Compare energy values and view optimized geometry

### **Export Results**
1. Click "XYZ File" to download coordinates
2. Click "PNG Image" to export visualization

---

## 🧪 Supported Elements & Interactions

### **Transition Metals**
- Iron (Fe), Cobalt (Co), Nickel (Ni)

### **Noble Metals**
- Copper (Cu), Palladium (Pd), Silver (Ag), Platinum (Pt), Gold (Au)

### **Interaction Potentials**
- Gupta many-body potential for metallic systems
- Lennard-Jones parameters for mixed interactions

### **Gupta Potential Equations**

The Gupta potential is a many-body potential designed specifically for metallic systems that captures the essential physics of metallic bonding:

**Cohesive Energy Term:**

$$E_{mb}^i = \left[ \sum_{j \neq i} \xi_{(a,b)}^2 \exp\left\{-2q_{(a,b)}\left(\frac{r_{ij}}{r_{(a,b)}^0} - 1\right)\right\} \right]^{1/2}}$$

**Repulsive Energy Term (Born-Mayer type):**

$$E_r^i = A_{(a,b)} \sum_{j \neq i} \exp\left[-p_{(a,b)}\left(\frac{r_{ij}}{r_{(a,b)}^0} - 1\right)\right]$$

**Total Cohesive Energy:**

$$E_c = \sum_i (E_r^i - E_{mb}^i)$$

**Parameters:**
- **$A_{(a,b)}$**: Repulsive energy scale for element pair (a,b) (eV)
- **$\xi_{(a,b)}$**: Cohesive energy scale for element pair (a,b) (eV)
- **$p_{(a,b)}, q_{(a,b)}$**: Range parameters for repulsive and cohesive terms
- **$r_{(a,b)}^0$**: Nearest-neighbor bulk interatomic distance for pair (a,b) (Å)
- **$r_{ij}$**: Distance between atoms $i$ and $j$ (Å)

---

## 🏗️ Project Structure

```
clusterWebLab/
├── app.py                 # Flask application & API endpoints
├── static/
│   ├── scripts/
│   │   └── script.js      # Frontend JavaScript logic
│   ├── styles.css         # Application styling
│   ├── src/
│   │   ├── optimizer.py   # Structure optimization engine
│   │   └── rnd_xyz.py     # Random cluster generator
│   └── examples/          # Sample XYZ files
├── templates/
│   └── index.html         # Main application interface
└── requirements.txt       # Python dependencies
```

---

## 🔬 Technical Details

### **Backend Architecture**
- **Flask**: RESTful API design with session management
- **APScheduler**: Automated cleanup of temporary files
- **NumPy/SciPy**: Numerical computations and optimizations
- **ASE**: Atomic Simulation Environment for molecular operations

### **Frontend Technologies**
- **3Dmol.js**: High-performance molecular visualization
- **Vanilla JavaScript**: Modern ES6+ features
- **CSS Grid**: Responsive layout system
- **Custom Notification System**: Real-time user feedback

### **Security Features**
- Session-based user isolation
- Secure file handling with validation
- Automatic cleanup of temporary files
- CSRF protection for all endpoints

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍🔬 Author

**ArturyLab** 🧪  
*Advanced Computational Chemistry Solutions*

- 🌐 **Website**: [Portafolio](https://arturylab.github.io/my-portafolio/)
- 📧 **Email**: arturylab@gmail.com
- 🐙 **GitHub**: [@arturylab](https://github.com/arturylab)

---

## 🙏 Acknowledgments

- **3Dmol.js Team** for the excellent molecular visualization library
- **ASE Community** for comprehensive atomic simulation tools
- **Flask Team** for the robust web framework
- **Open Source Community** for continuous inspiration and support

---

## 📈 Roadmap

- [ ] **Enhanced Optimization Algorithms** (DFT integration)
- [ ] **Multi-user Collaboration** features
- [ ] **Advanced Analysis Tools** (RDF, energy landscapes)
- [ ] **Mobile Application** for iOS/Android
- [ ] **Cloud Computing** integration for large-scale optimizations
- [ ] **Machine Learning** predictions for optimal structures

---

*Built with ❤️ for the computational chemistry community*
