# Kubernetes Runbook: CrashLoopBackOff

## 1. Problem

CrashLoopBackOff, Kubernetes'te bir container'ın başlatıldıktan sonra tekrar tekrar sonlanması ve Kubernetes'in yeniden başlatmalar arasında bekleme süresini artırması durumudur.

## 2. Olası Nedenler

- Uygulama başlangıç sırasında hata veriyor olabilir.
- Yanlış ortam değişkenleri veya eksik yapılandırma bulunabilir.
- Gerekli bir dosya ya da bağımlılık eksik olabilir.
- Container'ın bellek sınırı yetersiz olabilir.
- Uygulama yanlış komutla başlatılıyor olabilir.

## 3. İnceleme Adımları

Önce pod durumunu kontrol et:

```bash
kubectl get pods
```

Pod hakkında ayrıntılı bilgi al:

```bash
kubectl describe pod <pod-name>
```

Container'ın mevcut loglarını incele:

```bash
kubectl logs <pod-name>
```

Önceki container başlatmasının loglarını incele:

```bash
kubectl logs <pod-name> --previous
```

## 4. Çözüm Yaklaşımı

1. Loglarda görülen ilk hata mesajını belirle.
2. Gerekli ortam değişkenlerini ve yapılandırmaları kontrol et.
3. Uygulamanın başlangıç komutunu doğrula.
4. Bellek limitlerini ve Kubernetes olaylarını incele.
5. Sorunu giderdikten sonra pod durumunu tekrar kontrol et.

## 5. Güvenlik Notu

Loglar ve yapılandırmalar gizli bilgiler içerebilir. Parolaları, API anahtarlarını veya token değerlerini paylaşma. Sorunu araştırırken üretim ortamında değişiklik yapmadan önce etkiyi değerlendir.
