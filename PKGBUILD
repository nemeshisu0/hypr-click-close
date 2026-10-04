# Maintainer: nemeshisu <christianpertot07@gmail.com>
pkgname=hypr-click-close-git
pkgver=1.0.0
pkgrel=1
pkgdesc="Zero-overhead event-driven click-to-close daemon for Hyprland launchers (rofi, wofi, fuzzel, tofi, walker)"
arch=('any')
url="https://github.com/nemeshisu0/hypr-click-close"
license=('MIT')
depends=('hyprland' 'python')
provides=('hypr-click-close')
conflicts=('hypr-click-close')
source=("git+file://${PWD}")
sha256sums=('SKIP')

package() {
  install -Dm755 "${srcdir}/${pkgname%*}/hypr_click_close.py" "${pkgdir}/usr/bin/hypr-click-close"
  install -Dm644 "${srcdir}/${pkgname%*}/systemd/user/hypr-click-close.service" "${pkgdir}/usr/lib/systemd/user/hypr-click-close.service"
  install -Dm644 "${srcdir}/${pkgname%*}/LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 "${srcdir}/${pkgname%*}/README.md" "${pkgdir}/usr/share/doc/${pkgname}/README.md"
}
